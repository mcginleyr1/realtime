import os.path
import sys

import tornado.ioloop
import tornado.web

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from monetate.config import settings
import recorder

application = tornado.web.Application(
    handlers=[
        (r"/intelligence/(.*)", recorder.Recorder),
    ],
)

if __name__ == "__main__":
    application.listen(settings.COLLECTOR_PORT)
    tornado.ioloop.IOLoop.instance().start()
