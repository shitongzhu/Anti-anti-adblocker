import requests
import time
from lxml import html
from bs4 import BeautifulSoup
from param import *
import os
import copy
from ssl import SSLError
import re


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
    curr_site_js_dir = curr_site_dir + 'modified_js/'
    replace_res = open(curr_site_dir + 'replace_res', 'w+')
    if scripts_dict:
        for key, val in scripts_dict.iteritems():
            js_url = key
            print '[INFO][modify] Now modifying script/html ' + js_url + '...'
            modified_fname = 'modified_file_' + str(int(time.time() * 100))
            replace_res.write(js_url + ' -> ' + modified_fname + ' | ' + str(len(val)) + ' replacement(s)\n')
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
                    replace_res.write('[CondStmt]' + ' index: ' + str(idx) + ' | offset: ' + js_pos_cleaned + '\n')
                else:
                    source, begin, expr, idx = modify_expr(source, js_pos, is_condstmt=False)
                    if idx is None:
                        replace_res.write("ERROR: no 'if' condition at offset " + js_pos + ' found!\n')
                    else:
                        source = add_temp_var(source, begin, expr)
                        replace_res.write('expr: ' + expr + ' | index: ' + str(idx) + ' | offset: ' + js_pos + '\n')
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

    def convert_to_global(source, x, y, local_oft):
        glob = 0
        x, y, local_oft = int(x), int(y), int(local_oft)
        for i in range(x):
            glob += len(source.splitlines(True)[i])
        start_of_stmt = glob + y + local_oft
        while source[start_of_stmt].strip() != source[start_of_stmt]:
            start_of_stmt += 1
        return start_of_stmt

    # now that we already have the in-page index, this helper function is deprecated
    def is_html(source):
        tree = html.fromstring(source)
        if tree.tag == 'html':
            print '[INFO][modify] This is a HTML'
            return True
        elif tree.tag == 'p' or 'div':
            print '[INFO][modify] This is not a HTML'
            return False
        else:
            print '[ERROR][modify] Source type check failed: this document is of type ' + tree.tag

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
            idx = convert_to_global(source, x, y, stmt_offset)
            soup = BeautifulSoup(source, "lxml")
            scripts = soup.find_all('script')
            target_script_idx = len(scripts) - 1
            for i in range(len(scripts) - 1):
                if source.find(scripts[i].text) < idx < source.find(scripts[i + 1].text):
                    target_script_idx = i
            return source, None, None, target_script_idx
        else:
            return source, None, None, -1
    else:
        if x != 0 or y != 0:
            idx = convert_to_global(source, x, y, stmt_offset)
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
                if source.find(scripts[i].text) < idx < source.find(scripts[i + 1].text):
                    target_script_idx = i
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
        print '[INFO][modify] ' + expr + ' is the identified and extracted conditional expression'
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
