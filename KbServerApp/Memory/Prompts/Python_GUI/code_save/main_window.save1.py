import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from process_tab import ProcessTab
from memory_tab import MemoryTab
from log_tab import LogTab

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window")
        self.statusBar().showMessage('Ready')

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.process_tab = ProcessTab()
        self.memory_tab = MemoryTab()
        self.log_tab = LogTab()

        self.tab_widget.addTab(self.process_tab, "Process")
        self.tab_widget.addTab(self.memory_tab, "Memory")
        self.tab_widget.addTab(self.log_tab, "Log")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())