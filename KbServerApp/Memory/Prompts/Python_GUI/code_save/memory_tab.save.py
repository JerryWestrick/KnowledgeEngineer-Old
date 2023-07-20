from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit

class MemoryTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.edit = QTextEdit()
        self.layout.addWidget(self.edit)

        self.load_file()

    def load_file(self):
        with open('memory.txt', 'r') as f:
            self.edit.setText(f.read())
