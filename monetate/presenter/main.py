import os.path
import sys

import tornado.ioloop
import tornado.template
import tornado.web

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from monetate import PROJECT_ROOT

class MainHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('index.html', title='Foo')

application = tornado.web.Application(
    handlers=[(r"/", MainHandler),],
    template_path=os.path.join(PROJECT_ROOT, 'html'),
    # debug=True adds autoreload and recompiles templates on every request
    debug=True
)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

