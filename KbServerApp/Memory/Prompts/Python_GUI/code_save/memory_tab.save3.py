from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QTreeView, QSplitter, QDirModel
from PyQt5.QtCore import Qt

class MemoryTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.splitter = QSplitter(Qt.Horizontal)

        self.tree = QTreeView(self.splitter)
        self.model = QDirModel()
        self.tree.setModel(self.model)

        self.edit = QTextEdit(self.splitter)

        self.layout.addWidget(self.splitter)

        self.tree.clicked.connect(self.load_file)

    def load_file(self, index):
        path = self.model.filePath(index)
        with open(path, 'r') as f:
            self.edit.setText(f.read())