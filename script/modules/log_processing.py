import os
import re
from script.utils.SignatureMapping import SignatureMapping
from script.conf.param import *

log_rec_pattern = re.compile(NEW_PATTERN_LOG)


def regex_match(string, pattern):
    reg_match = re.match(pattern, string)
    if reg_match:
        reg_group = reg_match.groups()
        return reg_group
    else:
        return None


def pre_process_rmv_duplicate_ifs(curr_log_file):
    log = open(curr_log_file, 'r')
    trace_rec_list = log.readlines()
    log.close()

    trimmed_list = []
    ifed_sigs, idx_to_remove = set(), set()
    per_load_dict = {}

    for i in range(len(trace_rec_list)):
        rec_reg_group = regex_match(trace_rec_list[i], log_rec_pattern)
        if not rec_reg_group:
            idx_to_remove.add(i)
            continue

        trace_type = rec_reg_group[1]
        trace_sig = rec_reg_group[0] + ' ' + rec_reg_group[2]

        last_rec = per_load_dict.get(trace_sig)['last_rec'] if trace_sig in per_load_dict else -1
        last_pos = per_load_dict.get(trace_sig)['last_pos'] if trace_sig in per_load_dict else -1

        if trace_type == 'IF':
            if last_rec == IF:
                ifed_sig = regex_match(trace_rec_list[last_pos], log_rec_pattern)[0] + ' ' + \
                           regex_match(trace_rec_list[last_pos], log_rec_pattern)[2]
                ifed_sigs.add(ifed_sig)
                idx_to_remove.add(last_pos)
            per_load_dict[trace_sig] = {'last_rec': IF, 'last_pos': i}
        else:
            per_load_dict[trace_sig] = {'last_rec': NOT_IF, 'last_pos': i}

    for i in range(len(trace_rec_list)):
        if i not in idx_to_remove:
            trimmed_list.append(trace_rec_list[i])

    return trimmed_list, ifed_sigs


def pre_process_rmv_standalone_ifs(trace_rec_list, ifed_sigs):
    associated_ifs, standalone_ifs = set(), set()
    per_load_dict = {}
    trimmed_list = []

    for i in range(len(trace_rec_list)):
        rec_reg_group = regex_match(trace_rec_list[i], log_rec_pattern)
        trace_type = rec_reg_group[1]
        trace_sig = rec_reg_group[0] + ' ' + rec_reg_group[2]

        last_rec = per_load_dict[trace_sig]['last_rec'] if trace_sig in per_load_dict else -1
        last_pos = per_load_dict[trace_sig]['last_pos'] if trace_sig in per_load_dict else -1

        if trace_type == 'THEN' or trace_type == 'ELSE':
            if last_rec == IF:
                associated_ifs.add(last_pos)
            per_load_dict[trace_sig] = {'last_rec': NOT_IF, 'last_pos': i}
        elif trace_type == 'IF':
            per_load_dict[trace_sig] = {'last_rec': IF, 'last_pos': i}
        else:
            per_load_dict[trace_sig] = {'last_rec': NOT_IF, 'last_pos': i}

    for i in range(len(trace_rec_list)):
        rec_reg_group = regex_match(trace_rec_list[i], log_rec_pattern)
        trace_type = rec_reg_group[1]
        trace_sig = rec_reg_group[0] + ' ' + rec_reg_group[2]

        if trace_type == 'IF' and i not in associated_ifs:
            ifed_sigs.add(trace_sig)
            standalone_ifs.add(i)

    for i in range(len(trace_rec_list)):
        if i not in standalone_ifs:
            trimmed_list.append(trace_rec_list[i])

    return trimmed_list, ifed_sigs


def generate_per_load_sets(trace_rec_list, ifed_set):
    ifed, thened, elseed, condtrued, condfalsed, appeared, inconsistent = \
        ifed_set, set(), set(), set(), set(), set(), set()

    for i in range(len(trace_rec_list)):
        rec_reg_group = regex_match(trace_rec_list[i], log_rec_pattern)
        trace_type = rec_reg_group[1]
        trace_sig = rec_reg_group[0] + ' ' + rec_reg_group[2]

        if trace_type == 'THEN':
            thened.add(trace_sig)
        elif trace_type == 'ELSE':
            elseed.add(trace_sig)
        elif trace_type == 'ConditionalStatementTrue':
            condtrued.add(trace_sig)
        elif trace_type == 'ConditionalStatementFalse':
            condfalsed.add(trace_sig)

    appeared = ifed | thened | elseed | condtrued | condfalsed
    inconsistent = (ifed & thened) | (ifed & elseed) | (thened & elseed) | (condtrued & condfalsed)
    valid = appeared - inconsistent
    return valid, {'ifed': ifed & valid, 'thened': thened & valid, 'elseed': elseed & valid,
                   'condtrued': condtrued & valid, 'condfalsed': condfalsed & valid}


def process_per_setting(setting_dir, sig_mapping):
    log_files = []
    is_1st_log = True
    per_load_dict_pool = {}
    all_appeared, all_ifed, all_thened, all_elseed, all_condtrued, all_condfalsed = \
        set(), set(), set(), set(), set(), set()
    for file_name in os.listdir(setting_dir):
        log_files.append(setting_dir + file_name)
        per_load_dict_pool[file_name] = {}

    for log_path in log_files:
        pre_processed_1st, ifed = pre_process_rmv_duplicate_ifs(log_path)
        pre_processed_2nd, ifed = pre_process_rmv_standalone_ifs(pre_processed_1st, ifed)
        log_file = log_path.split('/')[-1]
        per_load_dict_pool[log_file] = {}
        per_load_dict_pool[log_file] = {'valid': set(), 'type_sets': {'ifed': set(), 'thened': set(), 'elseed': set(),
                                                                      'condtrued': set(), 'condfalsed': set()}}
        valid_full_sig, state_sets_full_sig = generate_per_load_sets(pre_processed_2nd, ifed)

        for sig in list(valid_full_sig):
            compact_sig = sig_mapping.map_to_compact(sig)
            per_load_dict_pool[log_file]['valid'].add(compact_sig)
        for key, value in state_sets_full_sig.iteritems():
            for sig in list(value):
                compact_sig = sig_mapping.map_to_compact(sig)
                per_load_dict_pool[log_file]['type_sets'][key].add(compact_sig)

    for log_path in log_files:
        valid, type_sets = per_load_dict_pool[log_path.split('/')[-1]]['valid'], \
                           per_load_dict_pool[log_path.split('/')[-1]]['type_sets']

        if is_1st_log:
            all_ifed = type_sets['ifed']
            all_thened = type_sets['thened']
            all_elseed = type_sets['elseed']
            all_condtrued = type_sets['condtrued']
            all_condfalsed = type_sets['condfalsed']
        else:
            all_ifed &= type_sets['ifed']
            all_thened &= type_sets['thened']
            all_elseed &= type_sets['elseed']
            all_condtrued &= type_sets['condtrued']
            all_condfalsed &= type_sets['condfalsed']
        is_1st_log = False

    all_appeared = all_ifed | all_thened | all_elseed | all_condtrued | all_condfalsed
    all_invalid = (all_ifed & all_thened) | (all_ifed & all_elseed) | \
                  (all_thened & all_elseed) | (all_condtrued & all_condfalsed)
    all_valid = all_appeared - all_invalid

    return all_valid, {'ifed': all_ifed & all_valid, 'thened': all_thened & all_valid, 'elseed': all_elseed & all_valid,
                       'condtrued': all_condtrued & all_valid, 'condfalsed': all_condfalsed & all_valid}


def report_diff(diff_dir, diff_dict, mapping):
    file_diff = open(diff_dir + '/diff_res', 'w')
    has_diff = False

    for diff_sig, diff_states in diff_dict.iteritems():
        has_diff = True
        if USE_SIG_MAPPING:
            diff_mark = "Unmatched: pos " + mapping.map_to_full(diff_sig) + " abp-on " + diff_states['wab'] \
                        + " abp-off " + diff_states['wab']
        else:
            diff_mark = "Unmatched: pos " + diff_sig + " abp-on " + diff_states['woab'] + " abp-off " + diff_states['woab']
        file_diff.write(diff_mark + '\n')
        print '[INFO][looper] ' + diff_mark

    if not has_diff:
        print "[INFO][looper] No unmatch detected!"
        file_diff.write('No unmatch detected!\n')

    file_diff.close()


def process(site_dir, mapping):
    def find_trace_type(sig):
        wab_state, woab_state = None, None
        for key, value in wab_sets.iteritems():
            if sig in value:
                wab_state = key
                break
        for key, value in woab_sets.iteritems():
            if sig in value:
                woab_state = key
                break
        return wab_state, woab_state

    diver_dict = {}

    wab_dir = site_dir + 'w_adblocker/'
    woab_dir = site_dir + 'wo_adblocker/'
    wab_valid, wab_sets = process_per_setting(wab_dir, mapping)
    woab_valid, woab_sets = process_per_setting(woab_dir, mapping)

    both_ifed = wab_sets['ifed'] & woab_sets['ifed']
    both_thened = wab_sets['thened'] & woab_sets['thened']
    both_elseed = wab_sets['elseed'] & woab_sets['elseed']
    both_condtrued = wab_sets['condtrued'] & woab_sets['condtrued']
    both_condfalsed = wab_sets['condfalsed'] & woab_sets['condfalsed']
    both_appeared = wab_valid & woab_valid

    final_inconsistent = both_appeared - (both_ifed | both_thened | both_elseed | both_condtrued | both_condfalsed)

    for diver_sig in list(final_inconsistent):
        diver_dict[diver_sig] = {'wab': find_trace_type(diver_sig)[0], 'woab': find_trace_type(diver_sig)[1]}

    return diver_dict


if __name__ == '__main__':
    cache = SignatureMapping()
    diff_dict = process(PATH_TO_FILTERED_LOG + 'bloomberg.com', cache)
    report_diff(PATH_TO_FILTERED_LOG + 'bloomberg.com', diff_dict, cache)
