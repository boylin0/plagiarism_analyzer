from flask import Flask, render_template, request
import utils as utils
import os
from worker import WorkerPool
from cache import clear_cache
from time import sleep

app = Flask(__name__)

_worker_pool = None

# analyze
@app.route('/api/run_analyze')
def analyze():
    path = request.args.get('path') or ''
    ratio = float(request.args.get('ratio')) or 0.9
    worker_count = int(request.args.get('workerCount')) or 8
    if not os.path.isdir(path):
        return { 'error': 'path is not a directory' }
    if not isinstance(ratio, float):
        return { 'error': 'ratio is not a float' }
    if ratio < 0.0 or ratio > 1.0:
        return { 'error': 'ratio is not in range 0.0-1.0' }
    clear_cache()
    global _worker_pool
    while _worker_pool is not None and not _worker_pool._allWorkerFinished():
        _worker_pool.StopWorker()
        sleep(0.5)
    _worker_pool = None
    _worker_pool = WorkerPool(path, ratio, worker_count)
    _worker_pool.StartWorker()
    return {'message': 'success'}  

# kill 
@app.route('/api/kill_analyze')
def kill_analyze():
    path = request.args.get('path') or ''
    global _worker_pool
    if _worker_pool is None:
        return { 'error': 'worker is not running' }
    while not _worker_pool._allWorkerFinished():
        _worker_pool.StopWorker()
        sleep(0.5)
    _worker_pool = None
    return {'message': 'success'}

# get progress
@app.route('/api/get_progress')
def get_progress():
    path = request.args.get('path') or ''
    global _worker_pool
    if _worker_pool is None:
        return { 'error': 'worker is not running' }
    progress = _worker_pool.getProgress()
    result = _worker_pool.getResult()
    return {
        'progress': progress,
        'result': result,
    }
    

# list system path
@app.route('/api/list_system_path')
def list_system_path():
    path = request.args.get('path') or ''
    result = {'abspath': os.path.abspath(path),  'data': []}
    # is dir
    if os.path.isdir(path):
        result = {
            'abspath': os.path.abspath(path),
            'folders': [os.path.basename(os.path.join(path, x)) for x in os.listdir(path) if os.path.isdir(os.path.join(path, x))],
        }
    return result


# read file
@app.route('/api/read_text')
def read_text():
    path = request.args.get('path') or ''
    normalized = request.args.get('normalized') or 'false'
    result = {'data': ''}
    # is file
    if os.path.isfile(path):
        content = utils.read_text_file(path)
        if normalized == 'true':
            content = utils.normalize_code(content)
        result = {
            'data': content
        }
    return result


# serve template
@app.route('/')
def index():
    return render_template('index.html')
