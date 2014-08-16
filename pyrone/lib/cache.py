"""
Caching wrapper: uses uwsgi caching framework if available or dummy internal dict
"""

try:
    import cPickle as pickle
except ImportError:
    import pickle

UWSGI = False
try:
    import uwsgi
    UWSGI = True
except ImportError:
    pass

# internal cache for setting values
_cache = {}


def set_value(key, value):
    if UWSGI:
        if uwsgi.cache_exists(key):
            uwsgi.cache_update(key, pickle.dumps(value))
        else:
            uwsgi.cache_set(key, pickle.dumps(value))
    else:
        _cache[key] = value


def get_value(key):
    value = None
    if UWSGI:
        value = uwsgi.cache_get(key)
        if value is not None:
            value = pickle.loads(value)
    else:
        if key in _cache:
            value = _cache[key]

    return value


def clear_cache():
    if UWSGI:
        uwsgi.cache_clear()
    else:
        _cache.clear()