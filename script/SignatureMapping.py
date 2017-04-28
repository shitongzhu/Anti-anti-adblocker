import re
from param import *


class SignatureMapping(object):
    def __init__(self):
        self.mapping_to_full, self.mapping_to_compact = dict(), dict()
        self.full_pattern = re.compile(FULL_SIGNATURE)
        self.compact_pattern = re.compile(COMPACT_SIGNATURE)

    def has_sig_in_full(self, sig):
        try:
            return self.mapping_to_full[sig] is not None
        except KeyError:
            return False

    def has_sig_in_compact(self, sig):
        try:
            return self.mapping_to_compact[sig] is not None
        except KeyError:
            return False

    def create_mapping(self, full_sig, compact_sig):
        self.mapping_to_compact[full_sig] = compact_sig
        self.mapping_to_full[compact_sig] = full_sig

    def map_to_compact(self, full_sig):
        group = re.match(self.full_pattern, full_sig).groups()
        compact_sig = group[0] + ' o' + group[3]
        self.create_mapping(full_sig, compact_sig)
        return compact_sig

    def map_to_full(self, compact_sig):
        assert isinstance(compact_sig, str)
        return self.mapping_to_full[compact_sig]
