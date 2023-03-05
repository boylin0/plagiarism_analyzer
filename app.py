from flask import Flask, render_template, request
import utils as utils
import os

app = Flask(__name__)

# analyze
@app.route('/api/analyze')
def analyze():
    path = request.args.get('path') or ''
    ratio = request.args.get('ratio') or 0.9
    ratio = float(ratio)
    if not os.path.isdir(path):
        return {
            'similar': []
        }
    if not isinstance(ratio, float):
        return {
            'similar': []
        }
    if ratio < 0 or ratio > 1:
        return {
            'similar': []
        }

    similar = utils.get_similar_files(path, ratio)
    return {
        'similar': similar
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
