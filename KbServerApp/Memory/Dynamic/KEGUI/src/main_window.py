from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget

from workbench_tab import WorkBenchTab
from log_tab import LogTab
from coms_tab import ComsTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window")

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.workbench_tab = WorkBenchTab()
        self.log_tab = LogTab()
        self.coms_tab = ComsTab()

        self.tab_widget.addTab(self.workbench_tab, "WorkBench")
        self.tab_widget.addTab(self.log_tab, "Log")
        self.tab_widget.addTab(self.coms_tab, "Coms")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()