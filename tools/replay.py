from __future__ import with_statement
from contextlib import closing

import boto
import boto.s3.key
import bz2
import optparse
import re
import simplejson
import tempfile
import urllib2

LOG_MATCHER = re.compile(
    "(?P<logdir>\w+)\D"
    "(?P<year>\d{4})\D"
    "(?P<month>\d{2})\D"
    "(?P<day>\d{2})\D"
    "(?P<instance>\w+)-"
    "(?P<type>\w+)-"
    "(?P<timestamp>\w+)"
    "\.log\.bz2\Z")

def parse_s3_uri(url):
    """
    Parse s3 url into (bucket, prefix) tuple.
    Supported urls:
        s3://bucket/prefix
        bucket:prefix
    """
    if url.startswith("s3://"):
        return url[5:].split('/', 1)
    return url.split(':', 1)

def get_track_data(line):
    """
     Track data is of the form:
     time, instance, track[pid][blah]: data
    """
    return simplejson.loads(line.split(' ', 3)[3])


def query_s3_track_set(uri):
    """
    Retrieve all files in an particular s3 buckets with a
    prefix matching the one in our uri.
    """
    urls = set()
    (bucket_name, key_prefix) = parse_s3_uri(uri)
    s3 = boto.connect_s3() # New connection for each s3 request
    bucket = s3.get_bucket(bucket_name, validate=False) # Do not list all keys in bucket
    for key in bucket.list(prefix=key_prefix):
        m = LOG_MATCHER.match(key.name)
        if m:
            d = m.groupdict()
            if d['type'] == 'session':
                urls.add( "s3://%s/%s" % (bucket_name, key.name) )
    return urls

def cat_key(line, key, value):
    """ Concat together the new value and the existing line """

    if value:
        if line:
            line = "%s&%s=%s" % (line, key, value)
        else:
            line = "%s=%s" % (key, value)
    return line


def create_line(account, add_to_cart, new_customer, grp, cid=None, purchase_value=None):
    line = ''
    line = cat_key(line, 'act', account)
    line = cat_key(line, 'cid', cid)
    line = cat_key(line, 'grp', grp)
    line = cat_key(line, 'atc', add_to_cart)
    line = cat_key(line, 'nc', new_customer)
    line = cat_key(line, 'pch', purchase_value)
    return line


def format_request_data(data):
    """
    Returns a string matching how our request should look
    """
    account = data['visitor']['account_id']
    add_to_cart = data['visit']['has_add_cart']
    new_customer = data['visit']['new_customer']
    purchases = data['session']['purchase']
    offers = data['session']['offer']
    grp = '0'
    if not offers:
        line = create_line(account, add_to_cart, new_customer, grp)
        yield '?%s' % line
    for offer in offers:
       grp = offer['grp']
       cid = offer['campaign_id']
       if not purchases:
           line = create_line(account, add_to_cart, new_customer, grp, cid)
           yield '?%s' % line
       for purchase in purchases:
            purchase_value = purchase.get('value', None)
            line = create_line(account, add_to_cart, new_customer, grp, cid)
            yield '?%s' % line

def main(s3_uri, ip):
    urls = query_s3_track_set(s3_uri)
    for url in urls:
        (bucket_name, key_name) = parse_s3_uri(url)
        s3 = boto.connect_s3()
        bucket = s3.get_bucket(bucket_name, validate=False)
        key = boto.s3.key.Key(bucket, key_name)
        with closing(tempfile.NamedTemporaryFile()) as tmp:
            key.get_file(tmp)
            tmp.seek(0)
            with closing(bz2.BZ2File(tmp.name)) as b:
                line = b.readline()
                while line:
                    data = get_track_data(line)
                    print data
                    for query_str in format_request_data(data):
                        record_url = "http://%s:8899/intelligence/%s" % (ip, query_str)
                        print record_url
                        urllib2.urlopen(record_url)
                    line = b.readline()


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('--uri', type='str', dest='uri', help="s3_uri to look for logs in.")
    parser.add_option('--ip', type='str', dest='ip', help="IP to hit with query")
    options, args = parser.parse_args()
    main(options.uri, options.ip)
