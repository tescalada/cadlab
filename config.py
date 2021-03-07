import os


class Config(object):
    # flask
    DEBUG = os.environ.get("DEBUG", False)
    TESTING = os.environ.get("TESTING", False)
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # wtforms
    WTF_CSRF_SECRET_KEY = os.environ.get("WTF_CSRF_SECRET_KEY")
    WTF_CSRF_ENABLED = False

    # Flask-cache
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "filesystem")
    CACHE_DEFAULT_TIMEOUT = os.environ.get("CACHE_DEFAULT_TIMEOUT", 300)
    CACHE_DIR = os.environ.get("CACHE_DIR", 'cache')
