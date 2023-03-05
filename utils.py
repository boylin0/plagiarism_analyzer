import difflib
import os
import hashlib
from cache import read_text_file_byCache

def similar_ratio(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def read_text_file(path):
    with open(path, 'r') as f:
        return f.read()


