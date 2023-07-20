import zlib
from twisted.internet import reactor, protocol
from twisted.protocols.basic import IntNStringReceiver


class TcpServer(IntNStringReceiver):
    structFormat = "!IB"  # unsigned 4-byte integer (message length) + unsigned 1-byte integer (flags)

    def __init__(self, factory):
        self.factory = factory
        self.connection_id: int = 0
        self.version: int = 0

    def connectionMade(self):
        print("Client connected")
        self.factory.addClient(self)

    def connectionLost(self, reason):
        print("Client disconnected")
        if not self.connection_id:
            self.factory.removeClient(self.connection_id)
            self.connection_id = 0

    def stringReceived(self, message):
        flags = message[0]  # Extract the bit flags from the received message
        payload = message[1:]  # Extract the payload from the received message

        if flags & 1:
            # First bit is set, indicating the message is compressed with zlib
            payload = zlib.decompress(payload)

        print("Received message from connection", self.connection_id, ":", payload.decode())

    def sendMessage(self, message, compressed=False):
        flags = 0
        if compressed:
            flags |= 1  # Set the first bit to indicate compression

        if compressed:
            message = zlib.compress(message)

        self.sendString(bytes([flags]) + message)

    def stringLengthReceived(self, messageLength):
        # The message length and flags have been received, now wait for the message payload
        self.expectedMessageLength = messageLength

    def processString(self, message):
        # Override this method to process the received message
        pass


class TcpServerFactory(protocol.Factory):
    def __init__(self):
        self.clients = {}  # Dictionary to store connected clients
        self.connection_counter = 0

    def buildProtocol(self, addr):
        return TcpServer(self)

    def addClient(self, client: TcpServer):
        self.connection_counter += 1
        self.clients[self.connection_counter] = client
        client.connection_id = self.connection_counter

    def removeClient(self, connection_id):
        if connection_id in self.clients:
            del self.clients[connection_id]

    def shutdown(self):
        print("Shutting down...")
        for connection_id, client in self.clients.items():
            client.sendMessage("Server is shutting down", compressed=False)
            client.transport.loseConnection()
        reactor.stop()


if __name__ == "__main__":
    factory = TcpServerFactory()

    # Start the server
    reactor.listenTCP(8000, factory)

    try:
        reactor.run()
    except KeyboardInterrupt:
        factory.shutdown()
