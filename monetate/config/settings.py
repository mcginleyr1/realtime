import os.path

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
STATIC_PATH = os.path.join(PROJECT_ROOT, 'static')
TEMPLATE_PATH = os.path.join(PROJECT_ROOT, 'templates')

DEFAULT_DSN = 'postgresql+psycopg2://user:password@host:port/dbname'

COLLECTOR_PORT = 8899
UI_PORT = 8889


