import argparse

from script.conf.param import *
from script.utils.utils import *
from script.modules.main import main_loop
from script.modules.work_queue import submit_urllist
from script.modules.worker import fetch_url

parser = argparse.ArgumentParser(description='Testing arg parser...')
parser.add_argument('--dlList', dest='DOWNLOAD_LIST', action='store_true')
parser.add_argument('--delRawLog', dest='DELETE_RAW_LOG', action='store_true')
parser.add_argument('--delOngRawLog', dest='DELETE_ONGOING_RAW_LOG', action='store_true')
parser.add_argument('--bkupOldLog', dest='BACKUP_OLD_LOG', action='store_true')
parser.add_argument('--revIncomLog', dest='REMOVE_INCOMPLETE_LOGS', action='store_true')
parser.add_argument('--run', dest='RUN_EXP', action='store_true')
parser.add_argument('--aggrRes', dest='AGGREGATE_EXP_RES', action='store_true')
parser.add_argument('--useCallStack', dest='USE_CALL_STACK', action='store_true')
parser.add_argument('--useCallStackWOft', dest='USE_CALL_STACK_WOFT', action='store_true')
parser.add_argument('--sbmtList', dest='DISTRIBUTE_URLLIST', action='store_true')
parser.add_argument('--fchURL', dest='FETCH_URL', action='store_true')
parser.add_argument('--behindProxy', dest='BEHIND_PROXY', action='store_true')
parser.add_argument('--useSigMapp', dest='USE_SIG_MAPPING', action='store_true')
parser.add_argument('--verifyRun', dest='VERIFY_RUN', action='store_true')
parser.add_argument('--browserID', dest='ID', action='store')
parser.add_argument('--hostID', dest='LIST_ID', action='store')
args = parser.parse_args()
for key, value in args.__dict__.iteritems():
    exec(key + ' = ' + str(value))

if __name__ == '__main__':
    path_to_logs = os.path.abspath(PATH_TO_FILTERED_LOG) + '/'

    if DISTRIBUTE_URLLIST:
        submit_urllist()

    if FETCH_URL:
        fetch_url()

    if REMOVE_INCOMPLETE_LOGS:
        for fname in os.listdir(path_to_logs):
            flag_deletable = False
            wab_dir = path_to_logs + fname + '/w_adblocker/'
            woab_dir = path_to_logs + fname + '/wo_adblocker/'
            try:
                for f in os.listdir(wab_dir):
                    if not os.path.getsize(wab_dir + f):
                        shutil.rmtree(path_to_logs + fname)
                        with open(PATH_TO_URLFILE, "a") as urllist:
                            urllist.write(fname + '\n')
                        print '[INFO][starter] ' + fname + ' is an incomplete log, to be deleted...'
                        flag_deletable = True
                        break
            except OSError:
                print '[ERROR][starter] ' + fname + ' does not have raw log folders, skipping...'
                continue
            if flag_deletable:
                continue
            try:
                for f in os.listdir(woab_dir):
                    if not os.path.getsize(woab_dir + f):
                        shutil.rmtree(path_to_logs + fname)
                        with open(PATH_TO_URLFILE, "a") as urllist:
                            urllist.write(fname + '\n')
                        print '[INFO][starter] ' + fname + ' is an incomplete log, to be deleted...'
                        flag_deletable = True
                        break
            except OSError:
                print '[ERROR][starter] ' + fname + ' does not have raw log folders, skipping...'
                continue
        finished_list = []
        for fname in os.listdir(path_to_logs):
            finished_list.append(fname)
        finished_set = set(finished_list)

    if BACKUP_OLD_LOG:
        try:
            os.rename(path_to_logs, path_to_logs + '_old_' + str(int(time.time() * 100)))
        except OSError:
            print '[ERROR][starter] ' + path_to_logs + ' has not been created yet'
            print '[INFO][starter] Creating a new one...'
            os.mkdir(path_to_logs)

    if DELETE_RAW_LOG:
        try:
            delete_raw_log(path_to_logs)
        except OSError:
            print '[ERROR][starter] ' + path_to_logs + ' has not been created yet, nothing to delete'

    if DOWNLOAD_LIST:
        downloaded_list = download_urllist(URL_TO_ALEXA_10K)
        downloaded_set = set(downloaded_list)
        real_set = downloaded_set - finished_set
        real_list = list(real_set)
        real_list = map(lambda lne: lne + '\n', real_list)
        with open(PATH_TO_URLFILE, 'w') as f:
            f.writelines(real_list)

    if RUN_EXP:
        main_loop()

    if AGGREGATE_EXP_RES:
        merge_log_files(PATH_TO_FILTERED_LOG, PATH_TO_MERGED_LOG)