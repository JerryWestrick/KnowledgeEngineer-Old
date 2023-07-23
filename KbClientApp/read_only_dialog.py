import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QTextEdit, QPushButton


class ReadOnlyDialog(QDialog):
    def __init__(self, title, text_content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)

        layout = QVBoxLayout(self)

        # Create a QTextEdit widget and set it as read-only
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlainText(text_content)
        self.text_edit.setReadOnly(True)

        # Create a button to close the dialog
        close_button = QPushButton('Close', self)
        close_button.clicked.connect(self.close)

        layout.addWidget(self.text_edit)
        layout.addWidget(close_button)


def main():
    app = QApplication(sys.argv)

    title = "Read-Only Dialog"
    text_content = "This is a read-only QTextEdit widget.\nYou cannot edit this text."

    dialog = ReadOnlyDialog(title, text_content)
    dialog.exec_()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
