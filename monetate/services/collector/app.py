import os.path
import sys

import tornado.ioloop
import tornado.web

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from monetate import PROJECT_ROOT

application = tornado.web.Application(
    handlers=[
        (r"/", handlers.MainHandler),
    ],
)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
