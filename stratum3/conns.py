import weakref

from stratum3 import services
from stratum3 import logger


log = logger.get_logger("conns")


class ConnectionRegistry(object):
    __connections = weakref.WeakKeyDictionary()

    @classmethod
    def add_connection(cls, conn):
        cls.__connections[conn] = True

    @classmethod
    def remove_connection(cls, conn):
        try:
            del cls.__connections[conn]
        except:
            log.exception("Warning: Cannot remove connection from ConnectionRegistry")

    @classmethod
    def get_session(cls, conn):
        if isinstance(conn, weakref.ref):
            conn = conn()

        if isinstance(conn, services.GenericService):
            conn = conn.connection_ref()

        if conn is None:
            return None

        return conn.get_session()

    @classmethod
    def iterate(cls):
        return cls.__connections.iterkeyrefs()
