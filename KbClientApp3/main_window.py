from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget

from workbench_tab import WorkBenchTab
from log_tab import LogTab, LOG
from coms_tab import ComsTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window")

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.workbench_tab = WorkBenchTab()
        self.log_tab = LogTab()
        self.coms_tab = ComsTab('ws://localhost:8080/ws')

        self.tab_widget.addTab(self.workbench_tab, "WorkBench")
        self.tab_widget.addTab(self.log_tab, "Log")
        self.tab_widget.addTab(self.coms_tab, "Coms")

    def log(self, action, message):
        LOG({'system': 'MainWindow', 'action': action, 'message': message})

    def delayed_function(self):
        # This function will be called after the GUI is shown
        self.log('showEvent', 'GUI is shown; connecting to remote server')
        self.coms_tab.webclient.connect_to_server()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    QTimer.singleShot(0, window.delayed_function)  # Delay execution until event loop starts
    app.exec()
