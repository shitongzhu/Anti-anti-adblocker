from main import *
from SignatureMapping import SignatureMapping
from param import *

if __name__ == '__main__':
    cache = SignatureMapping()
    site_dir1 = PATH_TO_FILTERED_LOG + 'xlovecash.com/w_adblocker/'
    site_dir2 = PATH_TO_FILTERED_LOG + 'xlovecash.com/wo_adblocker/'
    hashtable1 = log_differ(site_dir1, flag_mode=FLAG_W_AB, mapping=cache)
    hashtable2 = log_differ(site_dir2, flag_mode=FLAG_WO_AB, mapping=cache)
    #print hashtable1['__http://www.xlovecash.com/ o2']
    #print hashtable2['__http://www.xlovecash.com/ o2']
