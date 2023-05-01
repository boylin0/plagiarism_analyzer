import difflib
import os
import hashlib
from cache import read_text_file_byCache
import subprocess

def similar_ratio(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()

def read_text_file(path):
    # try utf-8
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        pass
    # try big5
    try:
        with open(path, 'r', encoding='big5') as f:
            return f.read()
    except:
        pass
    raise Exception('read file failed: ' + path)

def normalize_code(code):
    # llvm clang-format
    p = subprocess.Popen(['clang-format', '-style=gnu', '-sort-includes'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = p.communicate(code.encode('utf-8'))
    return out.decode('utf-8')

def make_relative_or_absolute_path(path):
    path = os.path.abspath(path)
    base_path = os.getcwd()
    if path.startswith(base_path):
        return '.' + path[len(base_path):]
    return path