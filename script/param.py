#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

# infer our browser id based on working directory
curr_path = os.getcwd()

# browser id
ID = curr_path[-1]

# paths
PATH_TO_CHROMIUM     = '../../releases/Release_' + ID + '/chrome'
PATH_TO_URLFILE      = 'res/scanning_list'
PATH_TO_LOG          = '/tmp/adblock_trace_' + ID + '.log'
PATH_TO_FILTERED_LOG = '../../logs/log_' + ID + '/'
PATH_TO_STAT_FILE    = '../../logs/total_stat'
PATH_TO_PROFILE      = '../../profiles/profile' + ID

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
#NUM_OF_RUNS_W_AB = 2
#NUM_OF_RUNS_WO_AB = 2
NUM_OF_RUNS = 3
N_TOP_ALEXA = 1000

# flags
FLAG_W_AB = 0
FLAG_WO_AB = 1

# regex pattern to match log record
PATTERN_LOG = r'\S* <String\[\d*\]: (http\S*)>\s(IF|THEN|ELSE)\s(\d*)(\s-1|)'
PATTERN_DIFF_REC = r'unmatched: pos (\S*) (\d*)'

# position-wise flags
THIS_POS_ONLY_HAS_IF = 0
THIS_POS_HAS_IF_THEN = 1
THIS_POS_HAS_IF_ELSE = 2

# timeout for loading pages (by sec)
TIMEOUT_LOAD_W_AB = 30
TIMEOUT_LOAD_WO_AB = 20

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

# URL for website list stored online
URL_TO_ADB_LIST = 'https://raw.githubusercontent.com/shadowysean/anti-adblocker-list/master/anti-adb-evaluation-list.txt'

# fake header
FAKE_HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2529.0 Safari/537.36'}
