import asyncio
import os
import sys

# Funky Stuff #1:  This needs to be done ASAP... or one of the twisted libs will define
#                  reactor for us, and the entire system will fail.
from twisted.internet import asyncioreactor
asyncioreactor.install(asyncio.get_event_loop())

# Funky Stuff #2:   Python by default adds the directory of the python script to the PythonPath.
#                   This allows us to include python from the same dir.
#                   When we start twistd.py as the starter script the current directory of the
#                   server.tac file is not appended, and all includes fail.  So we add it here!
# print(f"dir {os.getcwd()}")
# print(f"{os.environ.get('PYTHONPATH')}")

sys.path.append(os.getcwd())

# Rest of your server.tac content




from kbserver import KbServerProtocol

from autobahn.twisted import WebSocketServerFactory
from autobahn.twisted.resource import WebSocketResource
from twisted.internet import ssl, reactor, endpoints

from twisted.application import service, internet
from twisted.logger import Logger, LogLevel, LogLevelFilterPredicate, FilteringLogObserver, textFileLogObserver, \
    ILogObserver
from twisted.web.server import Site
from twisted.web.static import File

# skip database for now...
# from KbServerApp.sql_datastore import DatabaseStore, PostgresListenService

# The application we are building is...
log = Logger(namespace='Knowledge Engineer')
application = service.Application("Knowledge Engineer")

# Create static file http server using www directory
www_dir = "www-svelte/public"
# www_dir = "www"
root = File(www_dir)
log.info("Now serving {dir}", dir=www_dir)

factory = WebSocketServerFactory()
factory.protocol = KbServerProtocol
# factory.db = DatabaseStore(factory)  # interface to the Kb Database
factory.db = None  # Not using a database for now...
factory.webClients = []  # connected web sockets...
resource = WebSocketResource(factory)  # Communication is to be via websocket.
root.putChild(b"ws", resource)  # Add it to the http server as /ws folder.

# Create website
website = Site(root)

# Messy way to filter with logs...
info_predicate = LogLevelFilterPredicate(LogLevel.info)
log_observer = FilteringLogObserver(textFileLogObserver(sys.stdout), predicates=[info_predicate])
application.setComponent(ILogObserver, log_observer)

# Create SSL context factory
# context_factory = ssl.DefaultOpenSSLContextFactory('../ssl/private.key', '../ssl/certificate.pem')

# Create SSL server endpoint
endpoint = endpoints.serverFromString(reactor, "tcp:port=8080:interface=0.0.0.0")

# Listen on the SSL endpoint
endpoint_service = internet.StreamServerEndpointService(endpoint, website)
endpoint_service.setServiceParent(application)

# Using straight http:// protocol for now...
# www_server = internet.TCPServer(8090, website)  # Connect it to a Comm End Point
# www_server.setServiceParent(application)  # Register www server in Application
