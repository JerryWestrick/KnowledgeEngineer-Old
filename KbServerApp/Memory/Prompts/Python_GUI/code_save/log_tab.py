import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QMessageBox
from PyQt5.QtGui import QColor

class LogTab(QWidget):
    def __init__(self):
        super(LogTab, self).__init__()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.display_object)

        # Add items to the QListWidget. In a real application, these would be read from a log file.
        log_entries = [
            '{"name": "John", "age": 30, "city": "New York"}',
            '{"name": "Jane", "age": 25, "city": "Chicago"}',
            '{"name": "Bob", "age": 35, "city": "San Francisco"}'
        ]
        for i, entry in enumerate(log_entries):
            item = QListWidgetItem(entry)
            item.setForeground(QColor('red') if i % 2 else QColor('blue'))
            self.list_widget.addItem(item)

        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def display_object(self, item):
        obj = json.loads(item.text())
        obj_str = json.dumps(obj, indent=4)
        QMessageBox.information(self, "Log Entry", obj_str)
