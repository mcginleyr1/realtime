from sqlalchemy import MetaData, create_engine

import settings as settings

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
    
