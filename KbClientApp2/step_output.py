from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, \
    QAbstractItemView
from PyQt5.QtGui import QColor

from websocket import REGISTER_CALLBACK

empty_step = {
    "name": "",
    "prompt_name": "",
    "ai": {
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "max_tokens": 3000,
        "mode": "chat"
    },
    "storage_path": "",
    "messages": [],
    "response": {},
    "answer": "",
    "files": {},
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0,
    "sp_cost": 0.0,
    "sc_cost": 0.0,
    "s_total": 0.0,
    "elapsed_time": 0.0
}

class OutputTable(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.process_name = None
        self.step = None
        self.layout = QVBoxLayout(self)

        # Output Table
        self.output_table = QTableWidget()
        self.output_table.setColumnCount(2)
        self.output_table.setHorizontalHeaderLabels(["Attribute", "Value"])
        self.output_table.horizontalHeader().setStretchLastSection(True)
        self.output_table.horizontalHeader().setStyleSheet("::section { background-color: #ADD8E6 }")  # Setting color
        self.output_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.output_table.itemClicked.connect(self.row_selected)
        self.layout.addWidget(self.output_table)

        for key, value in empty_step.items():
            if key not in ["name", "prompt_name", "ai", "storage_path"]:
                row_position = self.output_table.rowCount()
                self.output_table.insertRow(row_position)
                self.output_table.setItem(row_position, 0, QTableWidgetItem(key))
                self.output_table.setItem(row_position, 1, QTableWidgetItem(str(value)))
        # REGISTER_CALLBACK(self, 'process_step_update')   # Should be handled by the process.py

    # def process_step_update(self, process_name, new_step):
    #     if self.process_name != process_name:
    #         return
    #     if self.step["name"] != new_step["name"]:
    #         return
    #     self.update_step(process_name, new_step)

    def row_selected(self, item):
        row = item.row()
        attribute = self.output_table.item(row, 0).text()  # Assuming the attribute is in the first column
        value = self.output_table.item(row, 1).text()  # Assuming the value is in the second column
        self.parent.output_editor.show_attribute_value(attribute, value)
        # print(f"Attribute: {attribute}, Value: {value}")

    def update_step(self, process_name: str, new_step):
        self.process_name = process_name
        self.step = new_step
        self.output_table.setRowCount(0)  # Clear the existing table
        self._fill_output_table()  # Update the table

    def _fill_output_table(self):
        # print(f"Call fill output table:  {self.step}")
        # Fill the output table with the new step
        for key in self.step.keys():
            if key not in ["name", "prompt_name", "ai", "storage_path"]:
                # print(f"Processing {key}>> {self.step[key]}")
                row_position = self.output_table.rowCount()
                self.output_table.insertRow(row_position)
                self.output_table.setItem(row_position, 0, QTableWidgetItem(key))
                self.output_table.setItem(row_position, 1, QTableWidgetItem(str(self.step[key])))

if __name__ == "__main__":
    app = QApplication([])
    display = OutputTable()
    display.show()
    app.exec_()
