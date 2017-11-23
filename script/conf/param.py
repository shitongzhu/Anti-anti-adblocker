#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import socket
import requests


# infer our browser id based on working directory
curr_path = os.getcwd()
curr_hostname = socket.gethostname()

# browser id
ID = curr_path[-1]
LIST_ID = curr_hostname[-2:]

# total num of instances
r = requests.get('https://raw.githubusercontent.com/shadowysean/anti-adblocker-list/master/conf')
NUM_OF_T_INS = int(r.text[:3])

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
NUM_OF_RUNS = 5
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
REPLACE_ENTRY     = r'type: (\S) \| expr: (.*) \| index: (\S*) \| offset: (\S*)'
CONTEXTUAL_URL    = r'(\S*)_(http\S*)'

# position-wise flags
THIS_POS_ONLY_HAS_IF = 0
THIS_POS_HAS_IF_THEN = 1
THIS_POS_HAS_IF_ELSE = 2
THIS_POS_HAS_COND_TRUE = 3
THIS_POS_HAS_COND_FALSE = 4

IF = 0
THEN = 1
ELSE = 2
COND = 3
COND_TRUE = 4
COND_FALSE = 5
INCONSISTENT = 6
NOT_IF = 7

# timeout for loading pages (by sec)
TIMEOUT_LOAD_W_AB = 45
TIMEOUT_LOAD_WO_AB = 45
TIMEOUT_LOAD_PRE_WARMING = 45

TIMEOUT_WARMING = 3

# command switches for starting Chromium with ABD enabled/disabled
OPT_W_AB = [PATH_TO_CHROMIUM, '--no-sandbox', '--user-data-dir=' + PATH_TO_PROFILE]
OPT_WO_AB = [PATH_TO_CHROMIUM, '--no-sandbox', '--disable-extensions', '--user-data-dir=' + PATH_TO_PROFILE]

ADDI_OPT_PROXY = ['--proxy-server=http://0.0.0.0:8080']

XVFB_PREF = "xvfb-run --server-args='-screen 0, 1024x768x24' "

# times of executing kill commands
KILL_TIMES = 5

# threshold parameters
DIFF_THRESHD_W_AB = 0
DIFF_THRESHD_WO_AB = 0
LF_THRESHD = 200

# URL for website list stored online
URL_TO_ADB_LIST = 'https://raw.githubusercontent.com/shadowysean/anti-adblocker-list/master/anti-adb-evaluation-list.txt'
#URL_TO_ALEXA_1M = 'https://raw.githubusercontent.com/shadowysean/anti-adblocker-list/master/top-1m-' + LIST_ID + '.txt'
URL_TO_ALEXA_10K = 'https://raw.githubusercontent.com/shadowysean/anti-adblocker-list/master/top-10ka'

# anti-adblocking solution database
ANTIADB_DATABASE = {
    'BlockAdblock': 'Place this code snippet near the footer of your page before the close of the /body tag',
    'FuckAdblock' : 'fuckadblock',
    'PageFair'    : 'asset.pagefair.com/measure.min.js',
    'Taboola'     : 'taboola.com',
    'XenForo'     : 'AdblockDetector/handler.min.js',
    'UOL family'  : 'Notamos que você tem um adblocker ligado :-'
}

# fake header
FAKE_HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2529.0 Safari/537.36'}

# start_experiment conf
DISTRIBUTE_URLLIST = False
FETCH_URL = False
DOWNLOAD_LIST = False
DELETE_RAW_LOG = False
DELETE_ONGOING_RAW_LOG = True
BACKUP_OLD_LOG = False
REMOVE_INCOMPLETE_LOGS = False
RUN_EXP = False
AGGREGATE_EXP_RES = True
USE_CALL_STACK = False
USE_CALL_STACK_WOFT = False
BEHIND_PROXY = False
USE_SIG_MAPPING = True
VERIFY_RUN = False
SAVE_SCRIPT_SNAPSHOT = False
DO_LOG_DIFF = False
GENERATE_DIFF_STAT = False
COMPRESS_RAW_LOG = True

DUMMY_LOG_RECORD = '_http://dummy.com/ IF x888y888o888'

DISPATCHER_HOST = 'ec2-52-53-162-48.us-west-1.compute.amazonaws.com'
