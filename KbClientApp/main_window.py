import argparse
import json
import sys

from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt5.QtWebSockets import QWebSocket, QWebSocketProtocol

from websocket import WebSocketClient
from process_tab import ProcessTab
from memory_tab import MemoryTab
from log_tab import LogTab, LOG


class MainWindow(QMainWindow):
    DatabaseStore = {}

    def __init__(self, memory_dir):
        super().__init__()

        # instantiate the Logger as soon as Possible

        self.setWindowTitle("Main Window")
        self.statusBar().showMessage('Ready')

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.process_tab = ProcessTab(self)
        self.memory_tab = MemoryTab(memory_dir, self)
        self.log_tab = LogTab(self)

        self.tab_widget.addTab(self.process_tab, "Process")
        self.tab_widget.addTab(self.memory_tab, "Memory")
        self.tab_widget.addTab(self.log_tab, "Log")

        # self.tab_widget.addTab(self.process_tab, "Process")
        # self.tab_widget.addTab(self.memory_tab, "Memory")
        # self.tab_widget.addTab(self.log_tab, "Log")

        self.websocket = WebSocketClient('ws://localhost:8090/ws', self)

        # self.websocket = QWebSocket()
        # self.websocket.connected.connect(self.on_websocket_connected)
        # self.websocket.disconnected.connect(self.on_websocket_disconnected)
        # self.websocket.error.connect(self.on_websocket_error)
        # self.websocket.textMessageReceived.connect(self.on_websocket_text_message)
        # self.websocket.binaryMessageReceived.connect(self.on_websocket_binary_message)
        # self.websocket.open(QUrl("ws://localhost:8090/ws"))

    def delayedFunction(self):
        # This function will be called after the GUI is shown
        if (LogTab.singleton is None):
            print("LogTab.singleton is None")
        else:
            print("LogTab.singleton is not None")
        self.log({'action': 'showEvent', 'message': 'GUI is shown; connecting to remote server'})
        self.websocket.connect_to_server()

    def log(self, message):
        message['system'] = 'main_window'
        LOG(message)
        # self.statusBar().showMessage(message)

    # def on_websocket_connected(self):
    #     self.log({'system': 'websocket', 'action': 'on_websocket_connected', 'message': 'WebSocket connected'})
    #
    # def on_websocket_disconnected(self):
    #     self.log({'system': 'websocket', 'action': 'on_websocket_disconnected', 'message': 'WebSocket disconnected'})
    #
    # def on_websocket_error(self, error_code):
    #     error_message = QWebSocketProtocol.closeReasonString(error_code)
    #     self.log(
    #         {'system': 'websocket', 'action': 'on_websocket_error', 'message': f'WebSocket error: {error_message}'})
    #
    # def on_websocket_text_message(self, message):
    #     obj = json.loads(message)
    #     self.log({'system': 'websocket', 'action': 'on_websocket_text_message', 'message': obj})
    #     if obj['cb'] == 'db_initial_load':
    #         # self.log({'system': 'user', 'action': f'db_initial_load from server {obj["cmd"]} of {obj["object"]}', 'message': 'db_initial_load'})
    #         self.DatabaseStore = obj['data']
    #
    #     elif obj['cb'] == 'db_async_notification':
    #         self.log({'system': 'user', 'action': f'db_async_notification from server {obj["cmd"]} of {obj["object"]}',
    #                   'message': 'db_async_notification'})
    #         if obj['cmd'] == 'I' or obj['cmd'] == 'U':
    #             self.DatabaseStore[obj['object']][obj['id']] = obj['record']
    #         elif obj['cmd'] == 'D':
    #             del self.DatabaseStore[obj['object']][obj['id']]
    #
    #     elif obj['cb'] == 'process_list_initial_load':
    #         self.process_tab.process_list_initial_load(obj['data'])
    #
    #     elif obj['cb'] == 'memory_initial_load':
    #         self.memory_tab.memory_initial_load(obj)
    #
    #     elif obj['cb'] == 'process_step_update':
    #         self.process_tab.process_step_update(obj)
    #
    #     elif obj['cb'] == 'memory_update':
    #         self.memory_tab.memory_update(obj)
    #
    #     else:
    #         self.log({'system': 'fail', 'action': obj['cb'],
    #                   'message': f"No Such Routine: {obj['cb']}(msg(cmd={obj['cmd']}, "
    #                              f"object={obj['object']}, rc={obj['rc']}, cb={obj['cb']}, data=...))", })
    #
    # def on_websocket_binary_message(self, message):
    #     text = message.data().decode('utf-8')
    #     self.log({'system': 'websocket', 'action': 'on_websocket_binary_message', 'message': text})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--memory', required=True, help='Directory for memory tab')
    args = parser.parse_args()

    app = QApplication(sys.argv)
    main = MainWindow(args.memory)
    main.show()
    QTimer.singleShot(0, main.delayedFunction)  # Delay execution until event loop starts
    sys.exit(app.exec_())
