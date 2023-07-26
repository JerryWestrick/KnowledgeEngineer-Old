import json

from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QAbstractSocket
from PyQt5.QtWebSockets import QWebSocket, QWebSocketProtocol
from log_tab import LOG


def SEND(message):
    WebSocketClient.connection.send_message(message)


class WebSocketClient(QWebSocket):
    Callbacks: dict[str, list[tuple[object, str]]] = {}
    connection = None

    def __init__(self, url, parent):
        super().__init__()

        self.url = url
        self.parent = parent

        # Connect signals
        self.connected.connect(self.on_connected)
        self.disconnected.connect(self.on_disconnected)
        self.textMessageReceived.connect(self.on_message_received)
        self.error.connect(self.on_error)
        WebSocketClient.connection = self

    def log(self, message):
        message['system'] = 'websocket'
        LOG(message)
        # self.statusBar().showMessage(message)

    def connect_to_server(self):
        self.open(QUrl(self.url))

    def on_connected(self):
        self.log({'action': 'on_websocket_connected', 'message': 'WebSocket connected'})

    def on_disconnected(self):
        self.log({'action': 'on_websocket_disconnected', 'message': 'WebSocket disconnected'})

    def on_message_received(self, message):
        obj = json.loads(message)
        self.log({'action': 'on_message_received', 'message': obj})
        cb = obj['cb']
        if cb in self.Callbacks:
            for (ins, method_name) in self.Callbacks[cb]:
                method = getattr(ins, method_name)
                method(obj)
        else:
            self.log({'action': 'Error',
                      'message': f"No Such Routine: {obj['cb']}(msg(cmd={obj['cmd']}, "
                                 f"object={obj['object']}, rc={obj['rc']}, cb={obj['cb']}, record={obj['record']}))", })

    def send_message(self, message):
        if self.state() == QAbstractSocket.ConnectedState:
            msg = json.dumps(message)
            self.sendTextMessage(msg)
            self.log({'action': 'send_message', 'message': message})
        else:
            self.log({'action': 'send_message', 'message': 'WebSocket not connected'})

    def close_connection(self):
        self.close()

    def on_error(self, error_code):
        error_message = self.errorString()
        self.log({'action': 'on_websocket_error', 'message': f'WebSocket error: {error_message}'})

    def on_websocket_binary_message(self, message):
        text = message.record().decode('utf-8')
        self.log({'action': 'on_websocket_binary_message', 'message': text})


def REGISTER_CALLBACK(obj, method_name):
    if method_name not in WebSocketClient.Callbacks:
        WebSocketClient.Callbacks[method_name] = []
    WebSocketClient.Callbacks[method_name].append((obj, method_name))


def DEREGISTER_CALLBACK(obj, method_name):
    if method_name in WebSocketClient.Callbacks:
        WebSocketClient.Callbacks[method_name].remove((obj, method_name))

