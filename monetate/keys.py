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

#Redis Keys
def get_campaign_key(campaign_id, metric):
    return campaign_key_patterns[metric] % {'campaign_id': campaign_id}

def get_add_to_cart_key(account, campaign, group):
    add_to_cart = '%s/add_to_cart/%s/%s'
    return add_to_cart % (account, campaign, group)

def get_bounce_rate_key(account, campaign, group):
    bounce_rate = "%s/bounce_rate/%s/%s"
    return bounce_rate  % (account, campaign, group)

def get_total_sales_key(account, campaign, group):
    total_sales = '%s/control_total_sales/%s/%s'
    return total_sales % (account, campaign, group)

def get_conversion_key(account, campaign, group):
    conversion = '%s/conversion/%s/%s'
    return conversion % (account, campaign, group)

def get_group_key(account, campaign, group):
    group_key = '%s/experiment_group/%s/%s'
    return group_key % (account, campaign, group)

def get_order_value_key(account, campaign, group):
    order_value = '%s/order_value/%s/%s'
    return order_value % (account, campaign, group)

def get_session_value_key(account, campaign, group):
    session_value = '%s/session_values/%s/%s'
    return session_value % (account, campaign, group)

def get_new_visitors_key(account):
    new_visitors = '%s/new_visitors'
    return new_visitors % account
