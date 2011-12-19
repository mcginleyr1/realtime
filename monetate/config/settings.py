import os.path

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
STATIC_PATH = os.path.join(PROJECT_ROOT, 'static')
TEMPLATE_PATH = os.path.join(PROJECT_ROOT, 'templates')

DEFAULT_DSN = 'postgresql+psycopg2://user:password@host:port/dbname'

<<<<<<< HEAD
REDIS_DSN = 'redis://localhost:6379/realtime'

COLLECTOR_PORT = 8888
=======
COLLECTOR_PORT = 8899
>>>>>>> b57d8bc098a4c3e01ee9a43f5208371cc97e71a4
UI_PORT = 8889


