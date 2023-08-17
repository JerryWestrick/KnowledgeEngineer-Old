from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView

from log_tab import LOG
from websocket import REGISTER_CALLBACK


class StepLog(QWidget):
    def __init__(self, workbench, step):
        self.table = None
        self.workbench = workbench
        super().__init__()

        self.init_ui()
        self.load_table(step)
        REGISTER_CALLBACK(self, method_list=['update_step'])

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Create a table widget with the number of rows equal to the number of keys in the step dictionary
        self.table = QTableWidget(9, 2)
        self.table.setHorizontalHeaderLabels(["Key", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.itemClicked.connect(self.item_clicked)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def log(self, action, message):
        LOG({'system': 'StepLog', 'action': action, 'message': message})

    def load_table(self, step):
        # Clear the table first
        self.table.setRowCount(0)

        # Fill the table with keys and values from the step dictionary
        for i, (key, value) in enumerate(step.items()):
            if key == 'ai':
                continue
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(key)))
            self.table.setItem(i, 1, QTableWidgetItem(str(value)))

        ai = step['ai']
        # Fill the table with keys and values from the ai dictionary
        last_row = self.table.rowCount()
        for i, (key, value) in enumerate(ai.items()):
            self.table.insertRow(last_row + i)
            self.table.setItem(last_row + i, 0, QTableWidgetItem(str(key)))
            self.table.setItem(last_row + i, 1, QTableWidgetItem(str(value)))

    def update_step(self, msg):
        # Load the new step into the table
        new_step = msg['record']
        self.log('update_step', f"step_update(...) Updating log values")
        self.load_table(new_step)

    def item_clicked(self, item):
        row = item.row()
        key_item = self.table.item(row, 0)  # Key is in the first column
        value_item = self.table.item(row, 1)  # Value is in the second column
        self.workbench.step_item_viewer.view_item(key_item.text(),value_item.text())
        # print(f'Row {row} clicked: Key="{key_item.text()}", Value="{value_item.text()}"')