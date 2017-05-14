#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import socket

# infer our browser id based on working directory
curr_path = os.getcwd()
curr_hostname = socket.gethostname()

# browser id
ID = curr_path[-1]
LIST_ID = curr_hostname[-1]

# paths
PATH_TO_CHROMIUM     = '../../releases/Release' + ID + '/chrome'
PATH_TO_URLFILE      = '../../res/urllist' + ID + '.txt'
PATH_TO_LOG          = '/tmp/adblockJSLog' + ID + '.txt'
PATH_TO_FILTERED_LOG = '../../logs/log' + ID + '/'
PATH_TO_STAT_FILE    = '../../logs/total_stat'
PATH_TO_PROFILE      = '../../profiles/profile' + ID + '/Default/'
PATH_TO_MERGED_LOG   = '../../logs/filterList' + ID + '.csv'

# signals
SIGSUCCESS = 1
SIGFAIL    = 0

# keywords
NO_KEYWORDS = [
    'extensions::',
    'chrome-extension:',
    'v8',
]
YES_KEYWORDS = [
    'http'
]

# number of runs stuff
NUM_OF_RUNS = 3
N_TOP_ALEXA = 1000

# flags
FLAG_W_AB = 0
FLAG_WO_AB = 1

# regex pattern to match log record
PATTERN_LOG       = r'\((\d*),(\d*)\) \S* <String\[\d*\]: ' \
                    r'(http\S*)>\s(IF|THEN|ELSE|ConditionalStatement|ConditionalStatementTrue|ConditionalStatementFalse)' \
                    r' (\d*)(\s-1|)'
NEW_PATTERN_LOG   = r'(\S*) (IF|THEN|ELSE|ConditionalStatement|ConditionalStatementTrue|ConditionalStatementFalse) ' \
                    r'(x\d*y\d*o\d*)'
PATTERN_DIFF_REC  = r'Unmatched: pos (\S*) (\S*) abp-on \[(\d*), set\(\[.*\]\)\] abp-off \[(\d*), set\(\[.*\]\)\]'
OFFSET_INFO       = r'(\[COND\])?x(\d*)y(\d*)o(\d*)'
RAW_OFFSET_INFO   = r'x(\d*)y(\d*)o(\d*)'
FULL_SIGNATURE    = r'(\S*) x(\d*)y(\d*)o(\d*)'
COMPACT_SIGNATURE = r'(\S*) o(\d*)'
REPLACE_TITLE     = r'(\S*) -> (\S*) \| (\d*) replacement\(s\)'
REPLACE_ENTRY     = r'expr: (.*) \| index: (\S*) \| offset: (\S*)'

# position-wise flags
THIS_POS_ONLY_HAS_IF = 0
THIS_POS_HAS_IF_THEN = 1
THIS_POS_HAS_IF_ELSE = 2
THIS_POS_HAS_COND_TRUE = 3
THIS_POS_HAS_COND_FALSE = 4

# timeout for loading pages (by sec)
TIMEOUT_LOAD_W_AB = 20
TIMEOUT_LOAD_WO_AB = 17

TIMEOUT_WARMING = 3

# command switches for starting Chromium with ABD enabled/disabled
OPT_W_AB = [PATH_TO_CHROMIUM, '--no-sandbox', '--user-data-dir=' + PATH_TO_PROFILE]
OPT_WO_AB = [PATH_TO_CHROMIUM, '--no-sandbox', '--disable-extensions', '--user-data-dir=' + PATH_TO_PROFILE]

XVFB_PREF = "xvfb-run --server-args='-screen 0, 1024x768x24' "

# times of executing kill commands
KILL_TIMES = 5

# threshold parameters
DIFF_THRESHD_W_AB = 0
DIFF_THRESHD_WO_AB = 0
LF_THRESHD = 200

# URL for website list stored online
URL_TO_ADB_LIST = 'https://raw.githubusercontent.com/shadowysean/anti-adblocker-list/master/anti-adb-evaluation-list.txt'
URL_TO_ALEXA_1M = 'https://raw.githubusercontent.com/shadowysean/anti-adblocker-list/master/top-1m-' + LIST_ID + '.txt'

# fake header
FAKE_HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2529.0 Safari/537.36'}
