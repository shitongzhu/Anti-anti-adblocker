#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
import time
import re
import shutil
from param import *
from utils import *
from SignatureMapping import SignatureMapping
import traceback


def url_reader(path_to_urllist):
    f = open(path_to_urllist, 'r')
    lst = f.readline()
    return lst.strip()


def url_loader(url, is_with_ext):
    is_warming = False if url else True
    if is_warming:
        print "[INFO][looper] Warming up Chromium..."
        if is_with_ext:
            args = OPT_W_AB
        else:
            args = OPT_WO_AB
    else:
        print "[INFO][looper] Visiting " + url
        if is_with_ext:
            args = OPT_W_AB + [url]
        else:
            args = OPT_WO_AB + [url]
    return subprocess.Popen(args=args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)


def log_extractor(path_to_log, flag_mode, url):
    def load(path_to_file):
        f = open(path_to_file, 'r')
        lst = f.readlines()
        f.close()
        return lst

    def unload(path_to_file, lst):
        f = open(path_to_file, 'w')
        f.writelines(lst)
        f.close()
        return

    def func_transform(line):
        reg_match = re.match(log_pattern, line)
        if reg_match:
            reg_group = reg_match.groups()
            script_url, stmt_type, position = \
                reg_group[2], reg_group[3], 'x' + reg_group[0] + 'y' + reg_group[1] + 'o' + reg_group[4]
            return script_url + ' ' + stmt_type + ' ' + position + '\n'
        else:
            return None

    def filter_by_kword(lst):
        return [func_transform(line) for line in lst if func_transform(line)]

    log = load(path_to_log)
    log_pattern = re.compile(PATTERN_LOG)
    filtered_log = filter_by_kword(log)

    if flag_mode == FLAG_W_AB:
        output_dir = (PATH_TO_FILTERED_LOG + url + '/w_adblocker/')
    else:
        output_dir = (PATH_TO_FILTERED_LOG + url + '/wo_adblocker/')
    output_path = output_dir + 'filtered_log_' + str(int(time.time() * 100)) + '.log'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    unload(output_path, filtered_log)
    return output_dir


def log_differ(path_to_dir, flag_mode, mapping):
    files = []
    grand_dict = {}
    run_count = 0
    log_pattern = re.compile(NEW_PATTERN_LOG)
    blklist = set()
    for fname in os.listdir(path_to_dir):
        files.append(path_to_dir + fname)

    def regex_match(line):
        reg_match = re.match(log_pattern, line)
        if reg_match:
            reg_group = reg_match.groups()
            return reg_group
        else:
            return None

    for f in files:
        run_count += 1
        log_file = open(f, 'r')
        lst = log_file.readlines()
        for idx in range(1, len(lst) - 1):
            reg_group_prev, reg_group_curr, reg_group_next = \
                regex_match(lst[idx - 1]), regex_match(lst[idx]), regex_match(lst[idx + 1])
            if reg_group_curr is None or reg_group_next is None or reg_group_prev is None:
                continue

            trace_key_curr = mapping.map_to_compact(reg_group_curr[0] + ' ' + reg_group_curr[2])
            trace_key_next = mapping.map_to_compact(reg_group_next[0] + ' ' + reg_group_next[2])
            trace_key_prev = mapping.map_to_compact(reg_group_prev[0] + ' ' + reg_group_prev[2])

            if reg_group_curr[1] == 'IF':
                if trace_key_curr != trace_key_next \
                        or (trace_key_curr == trace_key_next and reg_group_next[1] == 'IF'):
                    if grand_dict.get(trace_key_curr, -1) == -1:
                        grand_dict[trace_key_curr] = [THIS_POS_ONLY_HAS_IF, {run_count}]
                    else:
                        if grand_dict[trace_key_curr][0] != THIS_POS_ONLY_HAS_IF:
                            grand_dict[trace_key_curr][0] = THIS_POS_ONLY_HAS_IF
                            grand_dict[trace_key_curr][1].add(run_count)
                            blklist.add(trace_key_curr)
                        else:
                            grand_dict[trace_key_curr][1].add(run_count)
                else:
                    continue
            elif reg_group_curr[1] == 'THEN':
                if grand_dict.get(trace_key_curr, -1) == -1:
                    grand_dict[trace_key_curr] = [THIS_POS_HAS_IF_THEN, {run_count}]
                elif grand_dict[trace_key_curr][0] == THIS_POS_ONLY_HAS_IF and trace_key_curr != trace_key_prev\
                        and run_count in grand_dict[trace_key_curr][1]:
                    grand_dict[trace_key_curr][0] = THIS_POS_HAS_IF_THEN
                    blklist.discard(trace_key_curr)
                else:
                    if grand_dict[trace_key_curr][0] != THIS_POS_HAS_IF_THEN:
                        blklist.add(trace_key_curr)
                    else:
                        grand_dict[trace_key_curr][1].add(run_count)
            elif reg_group_curr[1] == 'ELSE':
                if grand_dict.get(trace_key_curr, -1) == -1:
                    grand_dict[trace_key_curr] = [THIS_POS_HAS_IF_ELSE, {run_count}]
                elif grand_dict[trace_key_curr][0] == THIS_POS_ONLY_HAS_IF and trace_key_curr != trace_key_prev\
                        and run_count in grand_dict[trace_key_curr][1]:
                    grand_dict[trace_key_curr][0] = THIS_POS_HAS_IF_ELSE
                    blklist.discard(trace_key_curr)
                else:
                    if grand_dict[trace_key_curr][0] != THIS_POS_HAS_IF_ELSE:
                        blklist.add(trace_key_curr)
                    else:
                        grand_dict[trace_key_curr][1].add(run_count)
            elif reg_group_curr[1] == 'ConditionalStatementTrue':
                if grand_dict.get(trace_key_curr, -1) == -1:
                    grand_dict[trace_key_curr] = [THIS_POS_HAS_COND_TRUE, {run_count}]
                else:
                    if grand_dict[trace_key_curr][0] != THIS_POS_HAS_COND_TRUE:
                        blklist.add(trace_key_curr)
                    else:
                        grand_dict[trace_key_curr][1].add(run_count)
            elif reg_group_curr[1] == 'ConditionalStatementFalse':
                if grand_dict.get(trace_key_curr, -1) == -1:
                    grand_dict[trace_key_curr] = [THIS_POS_HAS_COND_FALSE, {run_count}]
                else:
                    if grand_dict[trace_key_curr][0] != THIS_POS_HAS_COND_FALSE:
                        blklist.add(trace_key_curr)
                    else:
                        grand_dict[trace_key_curr][1].add(run_count)

    grand_dict_copy = grand_dict.copy()
    if flag_mode == FLAG_W_AB:
        threshold = DIFF_THRESHD_W_AB
    else:
        threshold = DIFF_THRESHD_WO_AB
    for key, val in grand_dict.iteritems():
        if key in blklist or run_count - len(val[1]) > threshold:
            del grand_dict_copy[key]
    return grand_dict_copy


def log_reporter(path_to_dir, dict_w_ab, dict_wo_ab, mapping):
    f = open(path_to_dir + 'diff_res', 'w')
    flag_flipping = False
    print "[INFO][looper] Starting log diff..."
    for key, value in dict_wo_ab.iteritems():
        curr_val = dict_w_ab.get(key, -1)
        if curr_val == -1:
            continue
        if curr_val[0] != value[0]:
            flag_flipping = True
            match_mark = "Unmatched: pos " + mapping.map_to_full(str(key)) + " abp-on " + str(dict_w_ab.get(key, -1)) \
                         + " abp-off " + str(dict_wo_ab.get(key, -1))
            f.write(match_mark + '\n')
            print '[INFO][looper] ' + match_mark
    if flag_flipping is False:
        print "[INFO][looper] No unmatch detected!"
        f.write('No unmatch detected!\n')
    f.close()


def main_loop():
    while url_reader(PATH_TO_URLFILE):
        try:
            url = url_reader(PATH_TO_URLFILE)
            try:
                shutil.rmtree(PATH_TO_FILTERED_LOG + url)
            except OSError as err:
                print "[INFO][looper] No existing directory"
            else:
                print "[INFO][looper] Deleted duplicate directory"

            for i in range(NUM_OF_RUNS):
                # 1st pass, with adblock enabled
                # tick its runtime
                p0 = url_loader(None, is_with_ext=True)
                time.sleep(TIMEOUT_WARMING)
                p1 = url_loader(url, is_with_ext=True)
                time.sleep(TIMEOUT_LOAD_W_AB)
                p0.kill()
                p1.kill()
                site_dir1 = log_extractor(PATH_TO_LOG, flag_mode=FLAG_W_AB, url=url)

                # 2nd pass, with adblock disabled
                p2 = url_loader(url, is_with_ext=False)
                time.sleep(TIMEOUT_LOAD_WO_AB)
                p2.kill()
                site_dir2 = log_extractor(PATH_TO_LOG, flag_mode=FLAG_WO_AB, url=url)
            cache = SignatureMapping()
            hashtable1 = log_differ(site_dir1, flag_mode=FLAG_W_AB, mapping=cache)
            hashtable2 = log_differ(site_dir2, flag_mode=FLAG_WO_AB, mapping=cache)
            curr_site_dir = PATH_TO_FILTERED_LOG + url + '/'
            log_reporter(curr_site_dir, hashtable1, hashtable2, mapping=cache)

            js_dict = single_log_stat_analyzer(curr_site_dir)
            dispatch_urls(js_dict, curr_site_dir)
            sync_list_file(PATH_TO_URLFILE)
            print '[INFO][looper] This site is done\n'
        except Exception as e:
            error_msg = '[FATAL][looper] ' + str(e)
            traceback.print_exc()
            print(error_msg + '\n')
            error_log = open(PATH_TO_FILTERED_LOG + url + '/error_log', 'w')
            error_log.write(str(error_msg))
            error_log.close()
            sync_list_file(PATH_TO_URLFILE)
            continue

    print '[INFO][looper] A batch of experiments are done!'


if __name__ == '__main__':
    main_loop()
