import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileSystemModel, QTreeView, QTextEdit, QSplitter
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.file_model = QFileSystemModel()
        self.file_model.setRootPath('')

        self.tree = QTreeView()
        self.tree.setModel(self.file_model)

        self.tree.clicked.connect(self.load_file)

        self.editor = QTextEdit()

        splitter = QSplitter()
        splitter.addWidget(self.tree)
        splitter.addWidget(self.editor)

        self.setCentralWidget(splitter)

    def load_file(self, index):
        file_path = self.file_model.filePath(index)
        with open(file_path, 'r') as file:
            data = file.read()
            self.editor.setText(data)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())