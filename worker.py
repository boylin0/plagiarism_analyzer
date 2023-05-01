import threading
import time
import utils as utils
from utils import similar_ratio
import difflib
import os
import hashlib
from cache import read_text_file_byCache

class WorkerPool:

    def __init__(self, path, target_ratio, worker_count):
        self._workers = []
        self.started = False
        self._target_ratio = target_ratio
        self._addWorker(worker_count)
        self._files_pair_total = 0
        self._files_pair = []
        self._files_pair_lock = threading.Lock()
        self._path = path
        self._prepare(path)
        self._result = []
        self._result_lock = threading.Lock()
        self._kill_signal = threading.Event()

    def _prepare(self, path):
        print('prepare files...')
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
        print('prepare files pair...')
        self._files_pair = []
        for i in range(len(files)):
            for j in range(i+1, len(files)):
                self._files_pair.append((files[i], files[j]))
        self._files_pair_total = len(self._files_pair)
        print('prepare files done' + str(len(self._files_pair)))

    def _addWorker(self, count):
        for i in range(count):
            t = threading.Thread(target=self._run)
            self._workers.append({
                'thread': t
            })

    def _allWorkerFinished(self):
        for w in self._workers:
            if w['thread'].is_alive():
                return False
        return True
    
    def getProgress(self):
        self._files_pair_lock.acquire()
        pair = self._files_pair
        self._files_pair_lock.release()
        if self.started:
            return {
                'total': self._files_pair_total,
                'current': self._files_pair_total - len(pair),
                'ratio': (self._files_pair_total - len(pair)) / self._files_pair_total,
            }
        else:
            return {
                'total': 0,
                'current': 0,
                'ratio': 0.0,
            }

    def getResult(self):
        if not self._allWorkerFinished():
            return None
        return self._result

    def _run(self):
        while True:
            if self._kill_signal.is_set():
                break
            self._files_pair_lock.acquire()
            if len(self._files_pair) == 0:
                self._files_pair_lock.release()
                break
            f1_path, f2_path = self._files_pair.pop()
            self._files_pair_lock.release()
            f1_content = read_text_file_byCache(f1_path)
            f2_content = read_text_file_byCache(f2_path)
            ratio = similar_ratio(f1_content, f2_content)
            ratio_normalized = similar_ratio(utils.normalize_code(f1_content), utils.normalize_code(f2_content))
            if ratio > self._target_ratio or ratio_normalized > self._target_ratio:
                self._result_lock.acquire()
                self._result.append({
                    'file1': f1_path.replace(self._path, ''),
                    'file2': f2_path.replace(self._path, ''),
                    'file1_abspath': f1_path,
                    'file2_abspath': f2_path,
                    'file1_size': os.path.getsize(f1_path),
                    'file2_size': os.path.getsize(f2_path),
                    'ratio': ratio,
                    'ratio_normalized': ratio_normalized,
                    'hash1': hashlib.md5(f1_content.encode('utf-8')).hexdigest(),
                    'hash2': hashlib.md5(f2_content.encode('utf-8')).hexdigest(),
                })
                self._result_lock.release()
                
    def StartWorker(self):
        self.started = True
        for w in self._workers:
            self._kill_signal.clear()
            w['thread'].start()

    def StopWorker(self):
        self._kill_signal.set()
