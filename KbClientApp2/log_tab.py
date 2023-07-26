import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt


class LogTab(QWidget):
    singleton = None  # public singleton for other classes to use

    colors = {
        'websocket': QColor('darkblue'),
        'step': QColor('darkgreen'),
        'main_window': QColor('darkorange'),
        'Process': QColor('darkmagenta'),
        'Prompt': QColor('darkorange'),
        'Error': QColor('red'),
    }

    # Singleton class wacky hacky
    def __new__(cls, *args, **kwargs):
        if not cls.singleton:
            cls.singleton = super().__new__(cls)
        return cls.singleton

    def __init__(self, parent):
        super(LogTab, self).__init__(parent)
        self.table_widget = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Removes padding
        layout.setSpacing(0)  # Removes spacing

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(['System', 'Action', 'Message'])

        self.table_widget.setColumnWidth(0, 100)  # set width of "System" column
        self.table_widget.setColumnWidth(1, 100)  # set width of "Action" column
        self.table_widget.horizontalHeader().setStretchLastSection(True)

        font = QFont()
        font.setPointSize(8)  # Set smaller font size
        self.table_widget.setFont(font)

        layout.addWidget(self.table_widget)
        self.setLayout(layout)

    def log(self, message: dict[str, str]):
        row = self.table_widget.rowCount()
        self.table_widget.insertRow(row)

        system_item = QTableWidgetItem(message['system'])
        system_item.setTextAlignment(Qt.AlignTop)
        self.table_widget.setItem(row, 0, system_item)

        action_item = QTableWidgetItem(message['action'])
        action_item.setTextAlignment(Qt.AlignTop)
        self.table_widget.setItem(row, 1, action_item)

        message_item = QTableWidgetItem(json.dumps(message['message']))
        message_item.setTextAlignment(Qt.AlignTop)
        self.table_widget.setItem(row, 2, message_item)

        color = self.colors[message['system']]
        if message['action'] == 'Error':
            color = self.colors['Error']

        # print(f">>{message}<<")
        msg = message['message']
        if type(msg) is dict:
            if 'rc' in msg and msg['rc'] == 'Fail':
                color = self.colors['Error']

        if type(msg) is str:
            if 'Error:' == msg[0:6]:
                color = self.colors['Error']

        for i in range(3):
            self.table_widget.item(row, i).setForeground(color)

    def display_object(self, item):
        obj = json.loads(item.text())
        obj_str = json.dumps(obj, indent=4)
        dialog = QMessageBox(f'{obj["system"]} - {obj["action"]}', obj_str, self)
        dialog.exec_()


def LOG(message: dict[str, any]):
    if LogTab.singleton is None:
        message['message'] = '...'
        print(f"LOG::LogTab.singleton is None: {message['system']}:{message['action']}")
        return
    LogTab.singleton.log(message)
