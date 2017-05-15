#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import operator
from time import gmtime, strftime
from param import *
#import alexa
from jsmodifier import *
import requests


def log_stat_collector(path_to_filtered_dir, path_to_stat_file):
    fstat = open(path_to_stat_file, 'w')
    fstat.write('\n\n--------- New Stats at Timestemp ' +
                strftime("%Y-%m-%d %H:%M:%S", gmtime()) +
                ' ---------\n')
    curr_positive, curr_negative = set(), set()
    for fname in os.listdir(path_to_filtered_dir):
        try:
            diff_file = open(path_to_filtered_dir + fname + '/diff_res', 'r')
        except IOError:
            print '[INFO][util] ' + fname + " is not yet finished"
            continue
        diff_content = diff_file.readlines()
        if diff_content[0] == 'No unmatch detected!\n':
            curr_negative.add(fname)
        else:
            curr_positive.add(fname)
        diff_file.close()
    fstat.write('\n>> Negative sites:\n')
    for r in list(curr_negative):
        fstat.write('-- ' + r + '\n')
    fstat.write('\n>> Positive sites:\n')
    for r in list(curr_positive):
        fstat.write('-- ' + r + '\n')
    fstat.write('\n---------- Stats Summary ----------\n')
    fstat.write('Total number of this run is '
                + str(len(curr_negative) + len(curr_positive)) + '\n')
    fstat.write('Total number of negative cases is '
                + str(len(curr_negative)) + '\n')
    fstat.write('Total number of positive cases is '
                + str(len(curr_positive)) + '\n')
    fstat.write('The positive rate is therefore '
                + str(len(curr_positive) / float(len(curr_negative) + len(curr_positive))) + '\n')
    fstat.write('----------- Stats Ends ------------')
    fstat.close()


'''
def dump_alexa_sites(top_n):
    urllist = alexa.top_list(top_n)
    urllist = zip(*urllist)[1]
    urllist = map(lambda lne: lne + '\n', urllist)
    with open(PATH_TO_URLFILE, 'w') as f:
        f.writelines(urllist)
    f.close()
'''


def download_urllist(url_to_list):
    r = requests.get(url=url_to_list)
    curr_id = ID
    urllist = r.text.split()
    urllist = map(lambda lne: lne + '\n', urllist)
    num_of_instances = len(os.listdir(os.getcwd() + '/../'))
    urllist = urllist[len(urllist) / num_of_instances *
        int(curr_id):len(urllist) / num_of_instances * (int(curr_id) + 1)]
    with open(PATH_TO_URLFILE, 'w') as f:
        f.writelines(urllist)
    f.close()


def log_stat_analyzer(path_to_filtered_dir):
    stat_log_pattern = re.compile(PATTERN_DIFF_REC)
    js_dict = dict()
    final_dict = dict()
    for fname in os.listdir(path_to_filtered_dir):
        try:
            diff_file = open(path_to_filtered_dir + fname + '/diff_res', 'r')
        except IOError:
            print '[ERROR][util] ' + fname + " is not yet finished"
            continue
        diff_content = diff_file.readlines()
        if diff_content[0] == 'no unmatch detected!\n':
            continue
        else:
            for l in diff_content:
                stat_reg_match = re.match(stat_log_pattern, l)
                stat_reg_group = stat_reg_match.groups()
                js_url = str(stat_reg_group[0])
                js_pos = str(stat_reg_group[1])
                if js_url not in js_dict:
                    js_dict[js_url] = dict()
                    js_dict[js_url][js_pos] = 1
                else:
                    if js_dict[js_url].get(js_pos, -1) == -1:
                        js_dict[js_url][js_pos] = 1
                    else:
                        js_dict[js_url][js_pos] += 1
        diff_file.close()
    for url, pos in js_dict.iteritems():
        final_dict[url] = sum(pos.itervalues())
    sorted_dict = sorted(final_dict.items(), key=operator.itemgetter(1))
    sorted_dict.reverse()
    '''
    c_gsy, c_gtm, c_gas = 0, 0, 0
    for [url, count] in sorted_dict:
        if 'googlesyndication' in url:
            c_gsy += count
        elif 'googletagmanager' in url:
            c_gtm += count
        elif 'jquery' in url:
            c_gas += count
    '''
    return js_dict
    #print c_gsy, c_gtm, c_gas


def single_log_stat_analyzer(path_to_site_dir):
    stat_log_pattern = re.compile(PATTERN_DIFF_REC)
    js_dict = dict()
    try:
        diff_file = open(path_to_site_dir + '/diff_res', 'r')
    except IOError:
        print '[INFO][util] ' + path_to_site_dir.split('/')[:-1] + " is not yet finished!"
        return None
    diff_content = diff_file.readlines()
    if diff_content[0] == 'No unmatch detected!\n':
        return None
    else:
        for l in diff_content:
            stat_reg_match = re.match(stat_log_pattern, l)
            stat_reg_group = stat_reg_match.groups()
            js_url = str(stat_reg_group[0])
            js_pos = str(stat_reg_group[1])
            js_type = int(stat_reg_group[2]) * int(stat_reg_group[3])
            if js_type > 4:
                js_pos = '[COND]' + js_pos
            if js_url not in js_dict:
                js_dict[js_url] = dict()
                js_dict[js_url][js_pos] = 1
            else:
                if js_dict[js_url].get(js_pos, -1) == -1:
                    js_dict[js_url][js_pos] = 1
                else:
                    js_dict[js_url][js_pos] += 1
    diff_file.close()
    return js_dict


def sync_list_file(path_to_urllist):
    with open(path_to_urllist, 'r') as fin:
        data = fin.read().splitlines(True)
    with open(path_to_urllist, 'w') as fout:
        fout.writelines(data[1:])


def merge_log_files(path_to_log_dir, path_to_aggr_log):
    aggr_log = open(path_to_aggr_log, 'w+')
    diff_res_entry = re.compile(PATTERN_DIFF_REC)
    replace_res_head = re.compile(REPLACE_TITLE)
    replace_res_entry = re.compile(REPLACE_ENTRY)
    offset_patt = re.compile(RAW_OFFSET_INFO)
    contextual_url = re.compile(CONTEXTUAL_URL)

    for fname in os.listdir(path_to_log_dir):
        site_dict = dict()
        rule_set = set()
        try:
            diff_file = open(path_to_log_dir + fname + '/diff_res', 'r')
        except IOError:
            print '[ERROR][util] ' + fname + " is not yet finished"
            continue
        diff_content = diff_file.readlines()
        if diff_content[0] == 'No unmatch detected!\n':
            continue
        else:
            for l in diff_content:
                diff_res_entry_match = re.match(diff_res_entry, l)
                diff_res_entry_group = diff_res_entry_match.groups()
                stmt_contextual_url, stmt_pos = diff_res_entry_group[0], diff_res_entry_group[1]

                contextual_url_group = re.match(contextual_url, stmt_contextual_url).groups()
                stmt_url = contextual_url_group[1]

                stmt_branch = 'true' if diff_res_entry_group[3] in {'1', '3'} else 'false'
                stmt_key = stmt_url + ' ' + stmt_pos
                stmt_value = stmt_branch
                site_dict[stmt_key] = stmt_value

        replace_file = open(path_to_log_dir + fname + '/replace_res', 'r')
        replace_content = replace_file.readlines()
        curr_line = 0
        while curr_line < len(replace_content) - 1:
            replace_res_head_match = re.match(replace_res_head, replace_content[curr_line])
            if not replace_res_head_match:
                curr_line += 1
                continue
            replace_res_head_group = replace_res_head_match.groups()
            stmt_url = replace_res_head_group[0]
            stmt_count = int(replace_res_head_group[2])
            for i in range(stmt_count):
                curr_line += 1
                replace_res_entry_match = re.match(replace_res_entry, replace_content[curr_line])
                if not replace_res_entry_match:
                    continue
                replace_res_entry_group = replace_res_entry_match.groups()
                stmt_type, stmt_expr, stmt_index, stmt_offset = \
                    replace_res_entry_group[0], replace_res_entry_group[1], replace_res_entry_group[2], replace_res_entry_group[3]
                stmt_key = stmt_url + ' ' + stmt_offset
                stmt_branch = site_dict[stmt_key]
                stmt_offset = re.match(offset_patt, stmt_offset).groups()[2]
                if stmt_type == 'i':
                    stmt_expr = stmt_expr[1:][:-1]
                rule = '"' + fname + '","' + stmt_url + '",' + stmt_index + ',' + stmt_offset + ',' + \
                       stmt_type + ',' + stmt_branch + ',"' + stmt_expr + '"\n'
                rule_set.add(rule)
            curr_line += 1
        aggr_log.writelines(list(rule_set))

    aggr_log.close()


if __name__ == '__main__':
    #log_stat_collector(PATH_TO_FILTERED_LOG, PATH_TO_STAT_FILE)
    #js_dict = single_log_stat_analyzer(PATH_TO_FILTERED_LOG + 'kbb.com')
    #print js_dict
    #dispatch_urls(js_dict)
    #dump_alexa_sites(N_TOP_ALEXA)
    #download_urllist(URL_TO_ALEXA_1M)
    merge_log_files(PATH_TO_FILTERED_LOG, PATH_TO_MERGED_LOG)
