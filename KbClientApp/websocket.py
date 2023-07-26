import json

from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QAbstractSocket
from PyQt5.QtWebSockets import QWebSocket, QWebSocketProtocol
from log_tab import LOG


def SEND(message):
    WebSocketClient.connection.send_message(message)


class WebSocketClient(QWebSocket):
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
        if obj['cb'] == 'db_initial_load':
            self.parent.DatabaseStore = obj['record']

        elif obj['cb'] == 'db_async_notification':
            self.log({'action': f'db_async_notification from server {obj["cmd"]} of {obj["object"]}',
                      'message': 'db_async_notification'})
            if obj['cmd'] == 'I' or obj['cmd'] == 'U':
                self.parent.DatabaseStore[obj['object']][obj['id']] = obj['record']
            elif obj['cmd'] == 'D':
                del self.parent.DatabaseStore[obj['object']][obj['id']]

        elif obj['cb'] == 'process_list_initial_load':
            self.parent.process_tab.process_list_initial_load(obj['record'])

        elif obj['cb'] == 'memory_initial_load':
            self.parent.memory_tab.memory_initial_load(obj)

        elif obj['cb'] == 'models_initial_load':
            self.parent.process_tab.models_initial_load(obj)

        elif obj['cb'] == 'process_step_update':
            self.parent.process_tab.process_step_update(obj)

        elif obj['cb'] == 'memory_update':
            self.parent.memory_tab.memory_update(obj)

        elif obj['cb'] == 'memory_test':
            self.parent.memory_tab.memory_test(obj)

        elif obj['cb'] == 'file_saved':
            self.parent.memory_tab.file_saved(obj)

        else:
            self.log({'action': obj['cb'],
                      'message': f"No Such Routine: {obj['cb']}(msg(cmd={obj['cmd']}, "
                                 f"object={obj['object']}, rc={obj['rc']}, cb={obj['cb']}, data={obj['record']}))", })

    def send_message(self, message):
        if self.state() == QAbstractSocket.ConnectedState:
            self.sendTextMessage(json.dumps(message))
        else:
            self.log(
                {'action': 'send_message', 'message': 'WebSocket not connected'})

    def close_connection(self):
        self.close()

    def on_error(self, error_code):
        error_message = self.errorString()
        self.log({'action': 'on_websocket_error', 'message': f'WebSocket error: {error_message}'})

    def on_websocket_binary_message(self, message):
        text = message.data().decode('utf-8')
        self.log({'action': 'on_websocket_binary_message', 'message': text})
