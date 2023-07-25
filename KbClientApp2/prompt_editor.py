from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton


class PromptEditor(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.file_name = 'None'
        self.file_value = ''
        self.filenameLabel = None
        self.textEditor = None
        self.init_ui()
        self.parent = parent

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a QLabel for the filename
        self.filenameLabel = QLabel("Filename: None")
        layout.addWidget(self.filenameLabel)

        # Create a QTextEdit
        self.textEditor = QTextEdit()
        layout.addWidget(self.textEditor)

        # Create an array of buttons
        buttons = ["Save", "Test"]

        # Create a QHBoxLayout for the buttons
        button_layout = QHBoxLayout()

        for button in buttons:
            button_layout.addWidget(QPushButton(button))

        # Add the button layout to the main layout
        layout.addLayout(button_layout)

        self.setWindowTitle('Prompt Editor')
        self.show()

    def file_selected(self, file_name, file_value):
        self.file_name = file_name
        self.file_value = file_value
        self.filenameLabel.setText(f"Filename: {self.file_name}")
        self.textEditor.setPlainText(self.file_value)

def main():
    app = QApplication([])
    ex = PromptEditor(None)
    app.exec_()


if __name__ == '__main__':
    main()
