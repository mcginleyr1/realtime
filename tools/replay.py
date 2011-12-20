from __future__ import with_statement
from contextlib import closing

import boto
import boto.s3.key
import decimal
import optparse
import re
import simplejson
import urllib2
import random

LOG_MATCHER = re.compile(
    "(?P<logdir>\w+)\D"
    "(?P<year>\d{4})\D"
    "(?P<month>\d{2})\D"
    "(?P<day>\d{2})\D"
    "(?P<instance>\w+)-"
    "(?P<type>\w+)-"
    "(?P<timestamp>\w+)"
    "\.log\.bz2\Z")

ACCT_CPG_MAP = {
    '129': ['1345', '2382', '2992'],
    '52': ['18494', '8329', '2938']
}


def get_track_data(line):
    """
     Track data is of the form:
     time, instance, track[pid][blah]: data
    """
    return simplejson.loads(line.split(' ', 3)[3])

def cat_key(line, key, value):
    """ Concat together the new value and the existing line """
    if value or value == '0':
        if line:
            line = "%s&%s=%s" % (line, key, value)
        else:
            line = "%s=%s" % (key, value)
    return line


def create_line(account, add_to_cart, new_customer, grp, purchase_value, cid, session_value=None ):
    line = ''
    line = cat_key(line, 'act', account)
    line = cat_key(line, 'cid', cid)
    line = cat_key(line, 'grp', grp)
    line = cat_key(line, 'atc', add_to_cart)
    line = cat_key(line, 'nc', new_customer)
    line = cat_key(line, 'pch', purchase_value)
    line = cat_key(line, 'st', session_value)
    return line


def format_request_data():
    """
    Returns a string matching how our request should look
    """
    account = ACCT_CPG_MAP.keys()[random.randint(0,1)]
    cid = ACCT_CPG_MAP[account][random.randint(0, 2)]
    add_to_cart = str(random.randint(0, 1))
    new_customer = str(random.randint(0, 1))
    grp = random.randint(0,1)
    session_total = 0;
    for i in range(0, 100):
        purchases = random.randint(0, 1)
        purchase_value = None
        if purchases:
            purchase_value = round(decimal.Decimal(str(random.uniform(0, 2000))), 2)
            session_total += purchase_value
        if i == 99:
            line = create_line(account, add_to_cart, new_customer, grp, purchase_value, cid, session_total)
        line = create_line(account, add_to_cart, new_customer, grp, purchase_value, cid)
        yield '?%s' % line
   
def main(ip):
    while True:
        for query_str in format_request_data():
            record_url = "http://%s:8899/intelligence/%s" % (ip, query_str)
            print record_url
            urllib2.urlopen(record_url)


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('--ip', type='str', dest='ip', help="IP to hit with query")
    options, args = parser.parse_args()
    main(options.ip)
