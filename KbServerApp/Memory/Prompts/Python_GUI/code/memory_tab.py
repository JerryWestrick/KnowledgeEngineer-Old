from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QTreeView, QSplitter, QDirModel
from PyQt5.QtCore import Qt

class MemoryTab(QWidget):
    def __init__(self, root_dir):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.splitter = QSplitter(Qt.Horizontal)

        self.tree = QTreeView(self.splitter)
        self.model = QDirModel()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(root_dir))

        for i in range(1, 4):
            self.tree.hideColumn(i)

        self.edit = QTextEdit(self.splitter)

        self.layout.addWidget(self.splitter)

        self.tree.clicked.connect(self.load_file)

    def load_file(self, index):
        path = self.model.filePath(index)
        with open(path, 'r') as f:
            self.edit.setText(f.read())