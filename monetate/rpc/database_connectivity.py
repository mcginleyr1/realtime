import backend.config.database as database
import sqlalchemy.orm as orm

class DatbaseConnectivity(object):
    """
    This class is inherited by all classes that need a sql alchemy engine/session object.
    """
    def __init__(self):
        self.database = database.Database()
        self.engine = self.database.get_engine()
        session_maker = orm.sessionmaker(bind=self.engine)
        self.session =  session_maker()
