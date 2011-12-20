import os.path
import sys

import tornado.ioloop
import tornado.web

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from monetate.config import settings
import handlers

application = tornado.web.Application(
    handlers=[
        (r"/", handlers.LandingHandler),
        (r"/metrics/(?P<account_id>\d+)/(?P<campaign_id>\d+)", handlers.MetricsHandler),
        (r"/d/metrics", handlers.CampaignMetricDataHandler)
    ],
    template_path=settings.TEMPLATE_PATH,
    static_path=settings.STATIC_PATH,
    # debug=True adds autoreload and recompiles templates on every request
    debug=settings.DEBUG
)

if __name__ == "__main__":
    application.listen(settings.UI_PORT)
    tornado.ioloop.IOLoop.instance().start()
