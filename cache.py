import utils as utils

MAX_CACHE_SIZE = 2000

_cache = {}

def read_text_file_byCache(file_path):
    global _cache
    if file_path not in _cache:
        _cache[file_path] = utils.read_text_file(file_path)
    if len(_cache) > MAX_CACHE_SIZE:
        for i in range(100):
            _cache.popitem()
            
    return _cache[file_path]
    
def clear_cache():
    global _cache
    _cache = {}