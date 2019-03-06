from twisted.internet import defer

from stratum3 import services
from stratum3 import exceptions
from stratum3 import logger


log = logger.get_logger('events')


class GenericEventHandler(object):
    def _handle_event(self, msg_method, msg_params, connection_ref):
        return defer.maybeDeferred(services.wrap_result_object,
                                   self.handle_event(msg_method, msg_params,
                                                     connection_ref))

    def handle_event(self, msg_method, msg_params, connection_ref):
        """In most cases you'll only need to overload this method."""

        log.info("Other side called method", msg_method, "with params", msg_params)
        raise exceptions.MethodNotFoundException(
            "Method '%s' not implemented" % msg_method)
