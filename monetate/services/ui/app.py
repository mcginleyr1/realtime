import os.path
import sys

import tornado.ioloop
import tornado.web

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from monetate import PROJECT_ROOT
import handlers

application = tornado.web.Application(
    handlers=[
        (r"/", handlers.MainHandler),
        (r"/wstest", handlers.ChartHandler)
    ],
    template_path=os.path.join(PROJECT_ROOT, 'html'),
    # debug=True adds autoreload and recompiles templates on every request
    debug=True
)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
