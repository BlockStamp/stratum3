from twisted.python import log
import stratum3.server
import stratum3.settings as settings

# This variable is used as an application handler by twistd 
application = stratum3.server.setup()

from twisted.internet import reactor

def heartbeat():
    log.msg('heartbeat')
    reactor.callLater(60, heartbeat)

if settings.DEBUG:
    reactor.callLater(0, heartbeat)
