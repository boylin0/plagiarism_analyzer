import difflib
import os
import hashlib
from cache import read_text_file_byCache

def similar_ratio(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def read_text_file(path):
    with open(path, 'r') as f:
        return f.read()


def get_similar_files(HW_DIR, target_ratio=0.9):

    print('check hw dir %s' % HW_DIR)

    # get all files
    print('get all files')
    files = []
    for root, dirs, fs in os.walk(HW_DIR):
        for f in fs:
            ignore = True
            if f.endswith('.c'):
                ignore = False
            if f.endswith('.cpp'):
                ignore = False
            if ignore:
                continue
            files.append(os.path.join(root, f))

    # check similar
    print('Analyzing similar files', end='', flush=True)
    similar = []
    for i in range(len(files)):
        for j in range(i+1, len(files)):
            f1_content = read_text_file_byCache(files[i])
            f2_content = read_text_file_byCache(files[j])
            ratio = similar_ratio(f1_content, f2_content)
            if ratio > target_ratio:
                similar.append({
                    'file1': files[i].replace(HW_DIR, ''),
                    'file2': files[j].replace(HW_DIR, ''),
                    'file1_abspath': files[i],
                    'file2_abspath': files[j],
                    'ratio': ratio,
                    'hash1': hashlib.md5(f1_content.encode('utf-8')).hexdigest(),
                    'hash2': hashlib.md5(f2_content.encode('utf-8')).hexdigest(),
                })
                print('.', end='', flush=True)

    # sort by ratio
    similar.sort(key=lambda x: x['ratio'], reverse=True)

    return similar
