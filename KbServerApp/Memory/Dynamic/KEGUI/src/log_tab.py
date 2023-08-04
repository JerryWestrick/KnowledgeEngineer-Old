from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class LogTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        label = QLabel("Log Tab")
        layout.addWidget(label)

        self.setLayout(layout)