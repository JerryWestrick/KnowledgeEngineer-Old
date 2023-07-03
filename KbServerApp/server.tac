import asyncio
import sys

from autobahn.twisted import WebSocketServerFactory
from autobahn.twisted.resource import WebSocketResource
from twisted.internet import asyncioreactor


# This needs to be done ASAP... or one of the twisted libs will define reactor
asyncioreactor.install(asyncio.get_event_loop())

from twisted.application import service, internet
from twisted.logger import Logger, LogLevel, LogLevelFilterPredicate, FilteringLogObserver, textFileLogObserver, \
    globalLogPublisher, ILogObserver
from twisted.web.server import Site
from twisted.web.static import File
from KbServerApp.kbserver import KbServerProtocol, DatabaseStore, PostgresListenService


# The application we are building is...
log = Logger(namespace='Knowledge Engineer')
application = service.Application("Knowledge Engineer")

# Create static file http server using www directory
root = File("www")

# Create websocket mess

factory = WebSocketServerFactory()  # factory to instantiate Protocol for each connection... global storage
factory.protocol = KbServerProtocol  # Protocol to instantiate
factory.db = DatabaseStore(factory)  # interface to the Kb Database
factory.webClients = []  # connected web sockets...
resource = WebSocketResource(factory)  # Communication is to be via websocket.
root.putChild(b"ws", resource)  # Add it to the http server as /ws folder.

# Create website
website = Site(root)

# Create a service to listen for postgresql notifications
notification_service = PostgresListenService(factory.db)
notification_service.setServiceParent(application)

# contextFactory = ssl.DefaultOpenSSLContextFactory('SSL_Keys/server.key',
#                                                   'SSL_Keys/server.crt')

# Ficky fucky with logs...
info_predicate = LogLevelFilterPredicate(LogLevel.info)
log_observer = FilteringLogObserver(textFileLogObserver(sys.stdout), predicates=[info_predicate])
application.setComponent(ILogObserver, log_observer)

# www_server = internet.SSLServer(8080, website, contextFactory)  # Connect it to a Comm End Point

# Using straight http:// protocol for now...
www_server = internet.TCPServer(8080, website)  # Connect it to a Comm End Point
www_server.setServiceParent(application)  # Register www server in Application
