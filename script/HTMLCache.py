import requests
from ssl import SSLError
from param import *
from bs4 import BeautifulSoup
import re


class HTMLCache(object):
    def __init__(self, path_to_dir=None, prev_cache=None):
        if not prev_cache:
            self.cache_dict = dict()
            self.cache_index = dict()
        else:
            self.cache_dict = prev_cache
        self.cwd = path_to_dir
        self.oldsig_pattern = re.compile(OLD_SIGNATURE)

    @staticmethod
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

    def has_url(self, url):
        try:
            return self.cache_dict[url] is not None
        except KeyError:
            return False

    def has_signature(self, sig):
        try:
            return self.cache_index[sig] is not None
        except KeyError:
            return False

    def get_html(self, url):
        if self.has_url(url):
            return self.cache_dict[url]
        else:
            self.cache_dict[url] = self.fetch_source(url)
            return self.cache_dict[url]

    @staticmethod
    def convert_to_global(source, x, y, local_oft):
        glob = 0
        x, y, local_oft = int(x), int(y), int(local_oft)
        for i in range(x):
            try:
                glob += len(source.splitlines(True)[i])
            except IndexError:
                print '[ERROR][cache] Weird out-of-range index occurs'
                return 0
        start_of_stmt = glob + y + local_oft
        while source[start_of_stmt].strip() != source[start_of_stmt]:
            start_of_stmt += 1
        return start_of_stmt

    def convert_to_index_if(self, source, x, y, local_oft):
        start_of_stmt = self.convert_to_global(source, x, y, local_oft)
        x, y, local_oft = int(x), int(y), int(local_oft)

        # back-up matching mechanism
        if source[start_of_stmt:start_of_stmt + 2] != 'if':
            target_script_idx = -1
            print "[ERROR][cache] Direct 'if' match failed, now secondary..."
            soup = BeautifulSoup(source, "lxml")
            scripts = soup.find_all('script')
            for i in range(len(scripts)):
                curr_script = scripts[i].text
                if local_oft + 2 > len(curr_script):
                    continue
                if curr_script[local_oft:local_oft + 2] == 'if':
                    target_script_idx = i
            if target_script_idx == -1:
                print "[ERROR][cache] No 'if' stmt accurately matched!"
                return -1
            else:
                return target_script_idx

        soup = BeautifulSoup(source, "lxml")
        scripts = soup.find_all('script')
        target_script_idx = len(scripts) - 1
        for i in range(len(scripts) - 1):
            if source.find(scripts[i].text) < start_of_stmt < source.find(scripts[i + 1].text):
                target_script_idx = i
        return target_script_idx

    def convert_to_index_condstmt(self, source, x, y, local_oft):
        start_of_stmt = self.convert_to_global(source, x, y, local_oft)
        soup = BeautifulSoup(source, "lxml")
        scripts = soup.find_all('script')
        target_script_idx = len(scripts) - 1
        for i in range(len(scripts) - 1):
            if source.find(scripts[i].text) < start_of_stmt < source.find(scripts[i + 1].text):
                target_script_idx = i
        return target_script_idx

    def get_index(self, source, url, x, y, local_oft, is_condstmt=False):
        intersig = url + ' ' + local_oft
        if self.has_signature(intersig):
            return self.cache_index[intersig]
        else:
            if is_condstmt:
                self.cache_index[intersig] = str(self.convert_to_index_condstmt(source, x, y, local_oft))
                return self.cache_index[intersig]
            else:
                self.cache_index[intersig] = str(self.convert_to_index_if(source, x, y, local_oft))
                return self.cache_index[intersig]

    def generate_signature(self, url, old_sig, trace_type):
        match = re.match(self.oldsig_pattern, old_sig)
        reg_group = match.groups()
        x, y, local_oft = reg_group[0], reg_group[1], reg_group[2]
        if x != '0' or y != '0':
            if trace_type in {'IF', 'THEN', 'ELSE'}:
                html = self.get_html(url)
                return url + ' i' + self.get_index(html, url, x, y, local_oft, is_condstmt=True) + 'o' + local_oft
            else:
                return url + ' i-1' + 'o' + local_oft
