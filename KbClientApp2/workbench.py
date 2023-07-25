import argparse
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget

from workbench_tab import WorkbenchTab
from log_tab import LogTab, LOG
from websocket import WebSocketClient


class MainWindow(QMainWindow):
    DatabaseStore = {}

    def __init__(self, connection: str):
        super().__init__()

        # instantiate the Logger as soon as Possible

        self.setWindowTitle("KnowledgeEngineer Workbench")
        self.statusBar().showMessage('Ready')

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.workbench_tab = WorkbenchTab(self)
        # self.memory_tab = MemoryTab(self)
        self.log_tab = LogTab(self)

        self.tab_widget.addTab(self.workbench_tab, "Workbench")
        # self.tab_widget.addTab(self.memory_tab, "Memory")
        self.tab_widget.addTab(self.log_tab, "Log")

        self.websocket = WebSocketClient(connection, self)

    def delayed_function(self):
        # This function will be called after the GUI is shown
        if LogTab.singleton is None:
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
    parser.add_argument('-c', '--connection', required=False, default='ws://localhost:8080/ws',
                        help='connection string to the server')
    args = parser.parse_args()

    app = QApplication(sys.argv)
    main = MainWindow(args.connection)
    main.show()
    QTimer.singleShot(0, main.delayed_function)  # Delay execution until event loop starts
    sys.exit(app.exec_())
