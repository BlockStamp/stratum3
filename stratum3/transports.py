from twisted.internet.protocol import ServerFactory

from stratum3 import events
from stratum3 import protos


class SocketTransportFactory(ServerFactory):
    def __init__(self, debug=False, signing_key=None, signing_id=None,
                 event_handler=events.GenericEventHandler,
                 tcp_proxy_protocol_enable=False):
        self.debug = debug
        self.signing_key = signing_key
        self.signing_id = signing_id
        self.event_handler = event_handler
        self.protocol = protos.Protocol

        # Read settings.TCP_PROXY_PROTOCOL documentation
        self.tcp_proxy_protocol_enable = tcp_proxy_protocol_enable
