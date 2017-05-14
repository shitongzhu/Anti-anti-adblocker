#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import time
from lxml import html
from bs4 import BeautifulSoup
from param import *
import os
import copy
from ssl import SSLError
import re
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def dispatch_urls(scripts_dict, curr_site_dir):
    def convert_to_global(source, x, y, local_oft):
        glob = 0
        x, y, local_oft = int(x), int(y), int(local_oft)
        for i in range(x):
            glob += len(source.splitlines(True)[i])
        start_of_stmt = glob + y + local_oft
        while source[start_of_stmt].strip() != source[start_of_stmt]:
            start_of_stmt += 1
        return start_of_stmt

    def regexp_offset(line):
        reg_match = re.match(offset_pattern, line)
        reg_group = reg_match.groups()
        return reg_group

    offset_pattern = re.compile(OFFSET_INFO)
    url_context = re.compile(CONTEXTUAL_URL)
    curr_site_js_dir = curr_site_dir + 'modified_js/'
    replace_res = open(curr_site_dir + 'replace_res', 'w+')
    if scripts_dict:
        for key, val in scripts_dict.iteritems():
            context_group = re.match(url_context, key).groups()
            context = context_group[0]
            js_url = context_group[1]
            print '[INFO][modify] Now modifying script/html ' + js_url + '...'
            modified_fname = 'modified_file_' + str(int(time.time() * 100))
            replace_res.write(js_url + ' -> ' + modified_fname + ' | ' + str(len(val)) + ' replacement(s) | ' +
                              'call stack: ' + context + '\n')
            source = fetch_source(js_url)
            source_copy = copy.copy(source)
            if source == -1:
                continue
            for pos, count in reversed(sorted(val.iteritems(), key=lambda (k, v): convert_to_global(
                source, regexp_offset(k)[1], regexp_offset(k)[2], regexp_offset(k)[3]))
            ):
                js_pos = pos
                js_pos_cleaned = 'x' + regexp_offset(js_pos)[1] + \
                                 'y' + regexp_offset(js_pos)[2] + \
                                 'o' + regexp_offset(js_pos)[3]
                print '[INFO][modify] Now we are at offset ' + js_pos + '...'

                # separate handling with conditional statements
                if regexp_offset(js_pos)[0] == '[COND]':
                    source, begin, expr, idx = modify_expr(source, js_pos, is_condstmt=True)
                    replace_res.write('type: t |' + ' expr: ' + expr + ' | index: ' + str(idx) + ' | offset: ' + js_pos_cleaned + '\n')
                else:
                    source, begin, expr, idx = modify_expr(source, js_pos, is_condstmt=False)
                    if idx is None:
                        replace_res.write("ERROR: no 'if' condition at offset " + js_pos + ' found!\n')
                    else:
                        source = add_temp_var(source, begin, expr)
                        expr = expr.replace(u'\u0022', u'\u005C\u0022')
                        expr = expr.replace(u"\u000A", u"\u005C\u005C\u006E")
                        expr = expr.replace(u"\u002C", u"\u005C\u002C")
                        replace_res.write('type: i |' + ' expr: ' + expr + ' | index: ' + str(idx) + ' | offset: ' + js_pos + '\n')
            replace_res.write('\n')

            if not os.path.exists(curr_site_js_dir):
                print '[INFO][modify] Now creating the folder ' + curr_site_js_dir + '...'
                os.mkdir(curr_site_js_dir)
            if source != source_copy:
                js_file = open(curr_site_js_dir + modified_fname, 'w+')
                js_file.write(source.encode('utf8'))
                js_file.close()
    else:
        print '[INFO][modify] No script to replace!'
    replace_res.close()


def fetch_source(url):
    try:
        r = requests.get(url=url, headers=FAKE_HEADER)
    except SSLError:
        print '[ERROR][modify] SSL error found, no response fetched!'
        return -1
    if r.status_code != 200:
        return -1
    else:
        return r.text


def modify_expr(source, stmt_offset, is_condstmt=False):
    def regexp_offset(line):
        reg_match = re.match(offset_pattern, line)
        reg_group = reg_match.groups()
        return reg_group

    def convert_to_global_if(source, x, y, local_oft):
        glob = 0
        x, y, local_oft = int(x), int(y), int(local_oft)
        for i in range(x):
            glob += len(source.splitlines(True)[i])
        start_of_stmt = glob + y + local_oft
        lf_count = 0
        while source[start_of_stmt:start_of_stmt + 2] != 'if' and lf_count <= LF_THRESHD:
            lf_count += 1
            start_of_stmt += 1
        return start_of_stmt

    def convert_to_global_cond(source, x, y, local_oft):
        glob = 0
        x, y, local_oft = int(x), int(y), int(local_oft)
        for i in range(x):
            glob += len(source.splitlines(True)[i])
        start_of_stmt = glob + y + local_oft
        while source[start_of_stmt:start_of_stmt + 1].isspace():
            start_of_stmt += 1
        return start_of_stmt

    stack = []
    target_script_idx = -1
    offset_pattern = re.compile(OFFSET_INFO)
    x, y, stmt_offset = int(regexp_offset(stmt_offset)[1]), \
                        int(regexp_offset(stmt_offset)[2]), \
                        int(regexp_offset(stmt_offset)[3])
    idx = stmt_offset

    # separate handling with conditional statement traces
    if is_condstmt:
        if x != 0 or y != 0:
            idx = convert_to_global_cond(source, x, y, stmt_offset)
            soup = BeautifulSoup(source, "lxml")
            scripts = soup.find_all('script')
            target_script_idx = len(scripts) - 1
            for i in range(len(scripts) - 1):
                if source.find(scripts[i].text) <= idx <= source.find(scripts[i].text) + len(scripts[i].text):
                    target_script_idx = i
                    break
            begin = idx
            while source[idx] != '?':
                idx += 1
            condition = source[begin:idx]
            print '[INFO][modify] ' + condition + ' -> extracted ternary condition'
            return source, begin, condition, target_script_idx
        else:
            begin = idx
            while source[idx] != '?':
                idx += 1
            condition = source[begin:idx]
            print '[INFO][modify] ' + condition + ' -> extracted ternary condition'
            return source, begin, condition, -1
    else:
        if x != 0 or y != 0:
            idx = convert_to_global_if(source, x, y, stmt_offset)
            if source[idx:idx + 2] != 'if':
                print "[ERROR][modify] Direct 'if' match failed, now secondary..."
                soup = BeautifulSoup(source, "lxml")
                scripts = soup.find_all('script')
                for i in range(len(scripts)):
                    curr_script = scripts[i].text
                    if stmt_offset + 2 > len(curr_script):
                        continue
                    if curr_script[stmt_offset:stmt_offset + 2] == 'if':
                        target_script_idx = i
                if target_script_idx == -1:
                    print "[ERROR][modify] No 'if' stmt accurately matched!"
                    return source, None, None, None
                else:
                    idx = stmt_offset + source.find(scripts[target_script_idx].text)
            soup = BeautifulSoup(source, "lxml")
            scripts = soup.find_all('script')
            target_script_idx = len(scripts) - 1
            for i in range(len(scripts) - 1):
                if source.find(scripts[i].text) <= idx <= source.find(scripts[i].text) + len(scripts[i].text):
                    target_script_idx = i
                    break

        while source[idx:idx + 2] != 'if':
            idx += 1
        while source[idx] != '(' and idx + 1 <= len(source):
            idx += 1
        begin = idx
        idx += 1
        stack.append(source[begin])
        while stack and idx < len(source):
            if source[idx] == '(':
                stack.append(source[idx])
            elif source[idx] == ')':
                if stack == [] or stack.pop() != '(':
                    print '[ERROR][modify] Invalid parenthesis!'
                    return -1
            idx += 1
        end = idx
        if stack:
            print '[ERROR][modify] Invalid parenthesis!'
            return -1
        expr = source[begin:end]
        source = source[:begin] + '(false)' + source[end:]
        print '[INFO][modify] ' + expr + ' -> extracted if condition'
        return source, begin, expr, target_script_idx


def add_temp_var(source, begin_idx, expr):
    idx = begin_idx
    while source[idx:idx + 2] != 'if':
        idx -= 1
        if idx < 0:
            print "[ERROR][modify] Beginning of the source reached, but no 'if' found!"
    source_modified = source[:idx] + 'temp_var_' + str(int(time.time() * 100)) + '=' + expr + '; ' + source[idx:]
    return source_modified

if __name__ == '__main__':
    modify_expr(requests.get('http://aiondatabase.net/us/').text, 'x729y33o5')
