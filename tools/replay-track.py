from __future__ import with_statement
from contextlib import closing

import boto
import boto.s3.key
import bz2
import optparse
import simplejson
import tempfilejj
import urllib2


TARGET_IP = ""

LOG_MATCHER = re.compile(
    "(?P<logdir>\w+)\D"
    "(?P<year>\d{4})\D"
    "(?P<month>\d{2})\D"
    "(?P<day>\d{2})\D"
    "(?P<instance>\w+)-"
    "(?P<type>\w+)-"
    "(?P<timestamp>\w+)"
    "\.log\.bz2\Z")

def parse_s3_url(url):
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
        m = matcher.match(key.name)
        if m:
            d = m.groupdict()
            if d['type'] == 'track':
                urls.add( "s3://%s/%s" % (bucket_name, key.name) )
    return urls

def format_request_data(data):
    """
    Returns a string matching how our request should look
    """
    pass

def main(s3_uri):
    urls = query_s3_track_set(s3_uri)
    for url in urls:
        (bucket_name, key_name) = parse_s3_url(filename)
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
                    query_str = format_request_data(data)
                    record_url = "http://%s:80/intelligence/%s" % (TARGET_IP, query_str)
                    urllib2.urlopen(record_url)
                    line = b.readline()


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option('--uri', type='str', dest='uri', help="s3_uri to look for logs in.")
    options, args = parser.parse_args()
    main(options.uri)