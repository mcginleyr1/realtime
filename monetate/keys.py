# Key names come from monetate_config.system_metrictypes.key

# addcart = Number of sessions with an add to cart / number of sessions
# bounce_rate = Number of sessions who view 1 page / number of sessions
# conversion = Sessions with purchase / number of sessions
# control_group = Total number of control sessions.
# experiment_group Total number of experiment sessions.
# ordervalue = Sum of purchase amounts / number of sessions with a purchase.
# session_value = Sum of purchase amounts / number of sessions

campaign_metrics = set([
    'addcart', 'bounce_rate', 'conversion', 'control_group',
    'control_totalsales', 'experiment_group', 'experiment_totalsales',
    'ordervalue', 'session_value'
])

campaign_key_patterns = {metric: '%(campaign_id)s/' + metric for metric in campaign_metrics}

def get_campaign_key(campaign_id, metric):
    return campaign_key_patterns[metric] % {'campaign_id': campaign_id}

