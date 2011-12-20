import os.path

# Passed along to tornado.
# If true, turns on autoload and templates are compiled on every request.
DEBUG=True

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
STATIC_PATH = os.path.join(PROJECT_ROOT, 'static')
TEMPLATE_PATH = os.path.join(PROJECT_ROOT, 'templates')

DEFAULT_DSN = 'postgresql+psycopg2://user:password@host:port/dbname'

REDIS_DSN = 'redis://localhost:6379/realtime'

COLLECTOR_PORT = 8899
UI_HOST = 'eps1-dev.monetate.net'
UI_PORT = 8889

try:
    from local_settings import *
except ImportError:
    pass
