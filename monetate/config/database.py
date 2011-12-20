import re

import brukva
import redis
from sqlalchemy import MetaData, create_engine

import settings as settings


class BaseRedis(object):
    REDIS_DSN_PAT = re.compile('^redis://(?P<host>.+):(?P<port>\d+)/(?P<db>.+)$')

    def _get_redis_conn_parts(self):
        """
        Return a dict of the redis host, port and db.
        """

        match = self.REDIS_DSN_PAT.match(self.conn_str)
        assert match

        return {'host': match.group('host'),
                'port': int(match.group('port')),
                'db': match.group('db')}

class Redis(BaseRedis):
    def __init__(self, conn_str=None):
        if conn_str:
            self.conn_str = conn_str
        else:
            self.conn_str = settings.REDIS_DSN

        redis_conn = self._get_redis_conn_parts()

        self.client = brukva.Client(
            host=redis_conn['host'],
            port=redis_conn['port'],
            selected_db=redis_conn['db']
        )

        self.client.connect()


class SyncRedis(BaseRedis):
    def __init__(self, conn_str=None):
        if conn_str:
            self.conn_str = conn_str
        else:
            self.conn_str = settings.REDIS_DSN

        redis_conn = self._get_redis_conn_parts()

        self.client = redis.StrictRedis(redis_conn['host'], redis_conn['port'])

class Database():
    """
    The single class/instance to return all of the database
    connection information
    """
    
    def __init__(self, conn_str=None):
        """
        Set up our database properties
        """
        if conn_str:
            self.conn_str = conn_str
        else:
            self.conn_str = settings.DEFAULT_DSN
        self.metadata = MetaData()
        self.engine = create_engine(self.conn_str, echo=True)


    def get_metadata(self):
        """
        Return the meta data object for use.
        """
        return self.metadata

    def get_engine(self):
        """
        Return the engine for use in querying.
        """
        return self.engine
    
