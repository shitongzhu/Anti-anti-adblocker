import requests
import time
from lxml import html
from bs4 import BeautifulSoup
from param import *
import os
import copy
from ssl import SSLError


def dispatch_urls(scripts_dict, curr_site_dir):
    '''
    def count_offset(text, script_idx, oft_before_tag, oft_after_tag):
        total_oft = 0
        text_by_line = text.splitlines()
        for i in range(script_idx):
            total_oft += text_by_line[i] + 1
        return total_oft + oft_before_tag + oft_after_tag
    '''
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
            for pos, count in reversed(sorted(val.iteritems())):
                js_pos = pos
                print '[INFO][modify] Now we are at offset ' + js_pos + '...'
                source, begin, expr, idx = modify_expr(source, js_pos)
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


def modify_expr(source, stmt_offset):
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
    stmt_offset = int(stmt_offset)
    idx = int(stmt_offset)
    if is_html(source):
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
    source_modified = source[:idx] + 'temp_var_' + str(int(time.time() * 100)) + '=' + expr + ';' + source[idx:]
    return source_modified

if __name__ == '__main__':
    modify_expr(requests.get('https://www.game-state.com/').text, 3493)
