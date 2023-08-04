import json

from PySide6.QtCore import QUrl
from PySide6.QtNetwork import QAbstractSocket
from PySide6.QtWebSockets import QWebSocket, QWebSocketProtocol

from log_tab import LOG


def SEND(message):
    WebSocketClient.connection.send_message(message)


class WebSocketClient(QWebSocket):
    Callbacks: dict[object, dict[str, any]] = {}
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
        self.stateChanged.connect(self.on_state_changed)
        WebSocketClient.connection = self

    def on_state_changed(self, state):
        self.log('state_changed', f'websocket({self.url})::{state}')
        self.parent.update_lights(state)

    def log(self, action, message):
        msg = {'system': 'websocket', 'action': action, 'message': message}
        LOG(msg)
        self.parent.append_log(msg)

    def connect_to_server(self):
        self.log('connect_to_server', f'WebSocket Connection to {self.url} Initiated')
        self.open(QUrl(self.url))

    def on_connected(self):
        self.log('on_websocket_connected', 'WebSocket connected')

    def on_disconnected(self):
        self.log('on_websocket_disconnected', 'WebSocket disconnected')

    def on_message_received(self, message):
        missing = True
        obj = json.loads(message)
        self.log('on_message_received', obj)
        cb = obj['cb']
        for module in self.Callbacks.keys():
            mod_cb_dict = self.Callbacks[module]
            if cb in mod_cb_dict:
                method = mod_cb_dict[cb]
                if method is not False:
                    method(obj)
                    missing = False
            else:
                method = getattr(module, cb, None)
                if callable(method):
                    mod_cb_dict[cb] = method
                    method(obj)
                    missing = False
                else:
                    mod_cb_dict[cb] = False

        if missing:
            self.log('on_message_received',
                     f"Error: No Such Routine: {obj['cb']}(msg(cmd={obj['cmd']}, "
                     f"object={obj['object']}, rc={obj['rc']}, cb={obj['cb']}, record={obj['record']}))")

    def send_message(self, message):
        if self.state() == QAbstractSocket.ConnectedState:
            msg = json.dumps(message)
            self.sendTextMessage(msg)
            self.log('send_message', message)
        else:
            self.log('send_message', 'Error: WebSocket not connected')

    def close_connection(self):
        self.close()

    def on_error(self, error_code):
        error_message = self.errorString()
        self.log('on_websocket_error', f'Error: {error_message}')

    def on_websocket_binary_message(self, message):
        text = message.record().decode('utf-8')
        self.log('on_websocket_binary_message', text)


# The register callback is a manual method connecting an object for callbacks.
# Note that the once registered for any callback.
# the object is used for all defined callbacks.
# Basically this is used for initial_xxx callbacks.
# @Todo: Register any obj that issues a SEND(), so that registration is only for initial... msgs.

def REGISTER_CALLBACK(obj, method_list: [str] = []):
    if obj not in WebSocketClient.Callbacks:
        WebSocketClient.Callbacks[obj] = {}
    module_cb_dict = WebSocketClient.Callbacks[obj]
    for method_name in method_list:
        method = getattr(obj, method_name, None)
        if callable(method):
            module_cb_dict[method_name] = method
        else:
            LOG({'system': 'websocket', 'action': 'REGISTER_CALLBACK', 'message': f'Error: Cannot call {method_name}'})
