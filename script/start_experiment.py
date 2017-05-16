import os
import sys
import time
from main import main_loop
from utils import *
from param import *

if __name__ == '__main__':
    path_to_logs = os.path.abspath(PATH_TO_FILTERED_LOG)
    if BACKUP_OLD_LOG:
        try:
            os.rename(path_to_logs, path_to_logs + '_old_' + str(int(time.time() * 100)))
        except OSError:
            print '[ERROR][starter] ' + path_to_logs + ' has not been created yet'
            print '[ERROR][starter] Creating a new one...'
            os.mkdir(path_to_logs)
    if DELETE_RAW_LOG:
        try:
            delete_raw_log(path_to_logs)
        except OSError:
            print '[ERROR][starter] ' + path_to_logs + ' has not been created yet, nothing to delete'
    if DOWNLOAD_LIST:
        download_urllist(URL_TO_ALEXA_10K)
    main_loop()
