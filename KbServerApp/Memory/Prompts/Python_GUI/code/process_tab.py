from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit

class ProcessTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.edit = QTextEdit()
        self.layout.addWidget(self.edit)

        self.load_file()

    def load_file(self):
        with open('process.txt', 'r') as f:
            self.edit.setText(f.read())