from flask import Flask, render_template, request
import utils as utils
import os
from worker import Worker
from cache import clear_cache

app = Flask(__name__)

# analyze
@app.route('/api/run_analyze')
def analyze():
    path = request.args.get('path') or ''
    ratio = request.args.get('ratio') or 0.9
    ratio = float(ratio)
    if not os.path.isdir(path):
        return { 'error': 'path is not a directory' }
    if not isinstance(ratio, float):
        return { 'error': 'ratio is not a float' }
    if ratio < 0.0 or ratio > 1.0:
        return { 'error': 'ratio is not in range 0.0-1.0' }
    clear_cache()
    return Worker.run(path, ratio)

# kill 
@app.route('/api/kill_analyze')
def kill_analyze():
    path = request.args.get('path') or ''
    result = Worker.kill(path)
    return result

# get progress
@app.route('/api/get_progress')
def get_progress():
    path = request.args.get('path') or ''
    progress = Worker.get_progress(path)
    result = Worker.get_result(path)
    if progress is None:
        return { 'error': 'worker is not running' }
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
    result = {'data': ''}
    # is file
    if os.path.isfile(path):
        result = {
            'data': open(path, 'r').read()
        }
    return result


# serve template
@app.route('/')
def index():
    return render_template('index.html')
