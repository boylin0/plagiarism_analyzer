import threading
import time
import utils as utils
from utils import similar_ratio
import difflib
import os
import hashlib
from cache import read_text_file_byCache

_workers = []

class Worker:
    
    @staticmethod
    def run(path, ratio):
        global _workers
        w = Worker._getWorker(path)
        if w is not None:
            if w['thread'].is_alive():
                return { 'error': 'worker is already running' }
            else:
                Worker._removeWorker(path)
        t = threading.Thread(target=Worker._run, args=(path, ratio))
        _workers.append({
            'path': path,
            'progress': None,
            'result': None,
            'thread': t,
        })
        t.start()
        return {'message': 'success'}

    @staticmethod
    def _run(path, target_ratio = 0.9):
        global _workers
        w = Worker._getWorker(path)
        # get all files
        files = []
        for root, dirs, fs in os.walk(path):
            for f in fs:
                ignore = True
                if f.endswith('.c'):
                    ignore = False
                if f.endswith('.cpp'):
                    ignore = False
                if ignore:
                    continue
                files.append(os.path.join(root, f))
        w['progress'] = {
            'total': 0,
            'current': 0,
            'ratio': 0.0,
        }
        # check similar
        similar = []
        w['progress']['total'] = len(files) * (len(files) - 1) / 2
        for i in range(len(files)):
            for j in range(i+1, len(files)):
                w['progress']['current'] += 1
                w['progress']['ratio'] = w['progress']['current'] / w['progress']['total']
                f1_content = read_text_file_byCache(files[i])
                f2_content = read_text_file_byCache(files[j])
                ratio = similar_ratio(f1_content, f2_content)
                if ratio > target_ratio:
                    similar.append({
                        'file1': files[i].replace(path, ''),
                        'file2': files[j].replace(path, ''),
                        'file1_abspath': files[i],
                        'file2_abspath': files[j],
                        'ratio': ratio,
                        'hash1': hashlib.md5(f1_content.encode('utf-8')).hexdigest(),
                        'hash2': hashlib.md5(f2_content.encode('utf-8')).hexdigest(),
                    })

        # sort by ratio
        similar.sort(key=lambda x: x['ratio'], reverse=True)
        w['result'] = similar

    @staticmethod
    def kill(path):
        w = Worker._getWorker(path)
        if w is None:
            return { 'error': 'worker is not running' }
        if w['thread'].is_alive():
            w['thread'].kill()
        return { 'message': 'success' }

    @staticmethod
    def _removeWorker(path):
        global _workers
        w = Worker._getWorker(path)
        _workers.remove(w)

    @staticmethod
    def _getWorker(path):
        global _workers
        for w in _workers:
            if w['path'] == path:
                return w
        return None

    @staticmethod
    def get_progress(path):
        w = Worker._getWorker(path)
        if w is None:
            return None
        return w['progress']

    @staticmethod
    def get_result(path):
        w = Worker._getWorker(path)
        if w is None:
            return None
        return w['result']
