import utils as utils

MAX_CACHE_SIZE = 1024 * 1024 * 1024 # 1GB

_cache = {}
_cache_size = 0

def read_text_file_byCache(file_path):
    global _cache, _cache_size
    if file_path not in _cache:
        _cache[file_path] = utils.read_text_file(file_path)
        _cache_size += len(_cache[file_path])
    if _cache_size > MAX_CACHE_SIZE:
        for i in range(100):
            _cache.popitem()
            
    return _cache[file_path]
    
def clear_cache():
    global _cache
    _cache = {}