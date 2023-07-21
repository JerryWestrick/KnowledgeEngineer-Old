import argparse
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget

from log_tab import LogTab, LOG
from memory_tab import MemoryTab
from process_tab import ProcessTab
from websocket import WebSocketClient


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

        self.websocket = WebSocketClient('ws://localhost:8090/ws', self)

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--memory', required=True, help='Directory for memory tab')
    args = parser.parse_args()

    app = QApplication(sys.argv)
    main = MainWindow(args.memory)
    main.show()
    QTimer.singleShot(0, main.delayedFunction)  # Delay execution until event loop starts
    sys.exit(app.exec_())
