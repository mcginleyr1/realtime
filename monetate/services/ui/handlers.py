import datetime
import logging

import tornado.ioloop
import tornado.web
import tornado.websocket

from monetate.config import database, settings
from monetate import keys as redis_keys


class LandingHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.redis_client = database.SyncRedis().client

        qvc_campaigns = self.redis_client.smembers(
            redis_keys.get_account_campaign_list_key(52))
        bb_campaigns = self.redis_client.smembers(
            redis_keys.get_account_campaign_list_key(129))

        self.render('index.html',
                    qvc_campaigns=qvc_campaigns,
                    bb_campaigns=bb_campaigns)


class MetricsHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('metrics.html',
                    ui_port=settings.UI_PORT,
                    ui_host=settings.UI_HOST,
                    account_id=kwargs['account_id'],
                    campaign_id=kwargs['campaign_id'])


class RedisWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self, *args, **kwargs):
        logging.debug('WebSocket opened, getting redis connection')

        self.redis_client = database.SyncRedis().client


    def on_close(self):
        logging.debug('WebSocket closed, closing redis connection')


class CampaignMetricDataHandler(RedisWebSocketHandler):
    # TODO: Use a separate IOLoop for the WebSocket stuff?

    paused = False

    def _get_add_to_cart_values(self,
        add_to_cart_count_control, add_to_cart_count_experiment,
        group_control,  group_experiment):

        if group_control and add_to_cart_count_control:
            add_to_cart_control = float(add_to_cart_count_control) / float(group_control)
        else:
            add_to_cart_control = None

        if group_experiment and add_to_cart_count_experiment:
            add_to_cart_experiment = float(add_to_cart_count_experiment) / float(group_experiment)
        else:
            add_to_cart_experiment = None

        return add_to_cart_control, add_to_cart_experiment

    def _get_session_value_values(self, account_id, campaign_id):
        def get_group_value(group):
            d = self.redis_client.hgetall(
                    redis_keys.get_session_value_key(account_id, campaign_id, group))

            try:
                count = d['count']

                if 'value' in d:
                    if count:
                        return float(d['value']) / float(count)
                    else:
                        return None
                else:
                    return 0
            except KeyError:
                return None

        control_value = get_group_value(redis_keys.GROUP_CONTROL)
        experiment_value = get_group_value(redis_keys.GROUP_EXPERIMENT)

        return control_value, experiment_value

    def _get_order_value_values(self, account_id, campaign_id):
        def get_group_value(group):
            d = self.redis_client.hgetall(
                    redis_keys.get_order_value_key(account_id, campaign_id, group))

            try:
                count = d['count']

                if 'value' in d:
                    if count:
                        return float(d['value']) / float(count)
                    else:
                        return None
                else:
                    return 0
            except KeyError:
                return None

        control_value = get_group_value(redis_keys.GROUP_CONTROL)
        experiment_value = get_group_value(redis_keys.GROUP_EXPERIMENT)

        return control_value, experiment_value


    def _send_metric_data_and_requeue(self, account_id, campaign_id):
        """
        If the WebSocket stream is still open then send the metric data
        and queue this method up again in the event loop.
        """
        def _requeue():
            tornado.ioloop.IOLoop.instance().add_timeout(
                datetime.timedelta(seconds=2),
                self.async_callback(self._send_metric_data_and_requeue, account_id, campaign_id)
            )

        if self.paused:
            _requeue()
        else:
            multi_results = self.redis_client.mget(
                [
                    redis_keys.get_group_key(account_id, campaign_id, redis_keys.GROUP_CONTROL),
                    redis_keys.get_group_key(account_id, campaign_id, redis_keys.GROUP_EXPERIMENT),
                    redis_keys.get_total_sales_key(account_id, campaign_id, redis_keys.GROUP_CONTROL),
                    redis_keys.get_total_sales_key(account_id, campaign_id, redis_keys.GROUP_EXPERIMENT),
                    redis_keys.get_add_to_cart_key(account_id, campaign_id, redis_keys.GROUP_CONTROL),
                    redis_keys.get_add_to_cart_key(account_id, campaign_id, redis_keys.GROUP_EXPERIMENT)
                ]
            )

            rps_control, rps_experiment = self._get_session_value_values(
                account_id, campaign_id)

            aov_control, aov_experiment = self._get_order_value_values(
                account_id, campaign_id)

            group_control = multi_results[0]
            group_experiment = multi_results[1]

            add_to_cart_control, add_to_cart_experiment = self._get_add_to_cart_values(
                multi_results[4], multi_results[5], group_control, group_experiment)

            data = {
                'group_control': group_control,
                'group_experiment': group_experiment,
                'total_sales_control': multi_results[2],
                'total_sales_experiment': multi_results[3],
                'order_value_control': aov_control,
                'order_value_experiment': aov_experiment,
                'add_to_cart_control': add_to_cart_control,
                'add_to_cart_experiment': add_to_cart_experiment,
                'session_control': rps_control,
                'session_experiment': rps_experiment
            }

            if self.stream.closed():
                pass
            else:
                self.write_message(data)

                _requeue()


    def on_message(self, message):
        """
        Called on sending of a WebSocket message from the client.
        We don't care what the message is, it's just a signal
        that we can start repeatedly sending the client metric data.
        """
        if message == 'pause':
            self.paused = (not self.paused)
        else:
            account_id, campaign_id = message.split('/')
            account_id = int(account_id)
            campaign_id = int(campaign_id)

            tornado.ioloop.IOLoop.instance().add_callback(
                self.async_callback(self._send_metric_data_and_requeue, account_id, campaign_id)
            )
