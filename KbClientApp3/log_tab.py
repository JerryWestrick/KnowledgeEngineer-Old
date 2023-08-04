import jsonpickle
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView


def get_color(message):
    colors = {
        'log': QColor('black'),
        'websocket': QColor('darkblue'),
        'StepEditor': QColor('darkgreen'),
        'MainWindow': QColor('darkorange'),
        'ProcessTree': QColor('darkmagenta'),
        'PromptTree': QColor('darkorange'),
        'PromptEditor': QColor('darkorange'),
        'Error': QColor('red'),
    }
    if message['action'] == 'Error':
        return colors['Error']
    if isinstance(message['message'], dict) and 'rc' in message['message'] and message['message']['rc'] == 'Fail':
        return colors['Error']
    if isinstance(message['message'], str) and message['message'].startswith('Error:'):
        return colors['Error']
    return colors.get(message['system'], Qt.black)  # Changed default color to black


class LogTab(QTableWidget):
    singleton = None

    # python singleton wacky hacky
    def __new__(cls, *args, **kwargs):
        if not cls.singleton:
            cls.singleton = super().__new__(cls)
        return cls.singleton

    def __init__(self):
        super().__init__()
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Timestamp", "System", "Action", "Message"])

        # Adjust the column widths as described
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        self.setStyleSheet(
            "QTableWidget {background-color: white; color: black;}")  # Set background color to white and font color to black

        self.setSortingEnabled(True)
        self.add_log_entry({'system': 'log', 'action': 'started', 'message': 'Logging System started'})

    def add_log_entry(self, message):
        timestamp = QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss.zzz')
        system = message['system']
        action = message['action']
        message_text = jsonpickle.dumps(message['message'])
        row_count = self.rowCount()
        self.insertRow(row_count)
        timestamp_item = QTableWidgetItem(timestamp)
        system_item = QTableWidgetItem(system)
        action_item = QTableWidgetItem(action)
        message_item = QTableWidgetItem(message_text)
        color = get_color(message)
        timestamp_item.setForeground(color)
        system_item.setForeground(color)
        action_item.setForeground(color)
        message_item.setForeground(color)
        self.setItem(row_count, 0, timestamp_item)
        self.setItem(row_count, 1, system_item)
        self.setItem(row_count, 2, action_item)
        self.setItem(row_count, 3, message_item)
        self.setRowHeight(row_count, 20)  # Change row height to reduce row spacing


def LOG(message):
    if LogTab.singleton is None:
        print(message)
        return
    LogTab.singleton.add_log_entry(message)
