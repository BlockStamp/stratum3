from twisted.application import service, internet
from twisted.internet import reactor

from stratum3 import services
from stratum3 import transports
from stratum3 import logger
from stratum3 import settings


log = logger.get_logger('server')


def setup(setup_event=None):
    try:
        from twisted.internet import epollreactor
        epollreactor.install()
    except ImportError:
        log.error("Failed to install epoll reactor, "
                  "default reactor will be used instead.")

    application = service.Application("stratum-server")

    if setup_event is None:
        setup_finalize(None, application)
    else:
        setup_event.addCallback(setup_finalize, application)

    return application


def setup_finalize(event, application):
    try:
        import signature
        signing_key = signature.load_privkey_pem(settings.SIGNING_KEY)
    except ImportError:
        log.error("Loading of signing key '%s' failed, "
              "protocol messages cannot be signed." % settings.SIGNING_KEY)
        signing_key = None

    # Set up thread pool size for service threads
    reactor.suggestThreadPoolSize(settings.THREAD_POOL_SIZE)

    transport = transports.SocketTransportFactory(
        debug=settings.DEBUG,
        signing_key=signing_key,
        signing_id=settings.SIGNING_ID,
        event_handler=services.ServiceEventHandler,
        tcp_proxy_protocol_enable=settings.TCP_PROXY_PROTOCOL)

    # Attach Socket Transport service to application
    socket = internet.TCPServer(settings.LISTEN_SOCKET_TRANSPORT, transport)
    socket.setServiceParent(application)
    return event


if __name__ == '__main__':
    print("This is not executable script. Try 'twistd -ny launcher.tac instead!")
