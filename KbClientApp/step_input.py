from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QPushButton, QComboBox, QDoubleSpinBox

from websocket import SEND
from log_tab import LOG


class InputTable(QWidget):
    model_keys = []

    def __init__(self, process_name, step, parent=None):
        super().__init__(parent)
        self.process_name = ''
        # Create the QVBoxLayout
        layout = QVBoxLayout()

        # AI Table in Input Group
        self.input_table = QTableWidget()
        # ... (rest of your code to set up the QTableWidget) ...

        # Add the QTableWidget to the layout
        layout.addWidget(self.input_table)

        # Create the QPushButton
        self.execute_button = QPushButton(f"Execute Step ")
        self.execute_button.clicked.connect(self.execute_selected_step)
        layout.addWidget(self.execute_button)

        # Set the layout of the InputTable widget
        self.setLayout(layout)

        self.input_table.setColumnCount(2)
        self.input_table.setHorizontalHeaderLabels(["Attribute", "Value"])
        self.input_table.horizontalHeader().setStretchLastSection(True)
        self.input_table.horizontalHeader().setStyleSheet("::section { background-color: #9ACD32 }")  # Setting color
        self.input_table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents)  # Set row height to fit contents

        self.update_step(process_name, step)

    def log(self, message):
        message['system'] = 'step'
        LOG(message)

    def update_step(self, process_name: str, new_step):

        self.process_name = process_name
        # Clear the existing table
        self.input_table.setRowCount(0)

        # Update the step
        self.step = new_step

        # Update the table
        self._fill_input_table()

        self.execute_button.setText(f"Execute {self.step['name']}")

    def _fill_input_table(self):
        # Fill the input table with the new step
        for key in ["name", "prompt_name", "storage_path"]:
            row_position = self.input_table.rowCount()
            self.input_table.insertRow(row_position)
            item = QTableWidgetItem(key)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.input_table.setItem(row_position, 0, item)
            self.input_table.setItem(row_position, 1, QTableWidgetItem(str(self.step[key])))

        for key, value in self.step["ai"].items():
            row_position = self.input_table.rowCount()
            self.input_table.insertRow(row_position)
            item = QTableWidgetItem(key)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.input_table.setItem(row_position, 0, item)
            if key == "model":
                self.model_combobox = QComboBox()
                self.model_combobox.addItems(self.model_keys)
                self.model_combobox.setCurrentText(str(value))
                self.model_combobox.currentTextChanged.connect(self.update_model_value)
                self.input_table.setCellWidget(row_position, 1, self.model_combobox)
            elif key == "mode":
                self.mode_combobox = QComboBox()
                self.mode_combobox.addItems(["chat", "complete"])
                self.mode_combobox.setCurrentText(str(value))
                self.mode_combobox.currentTextChanged.connect(self.update_mode_value)
                self.input_table.setCellWidget(row_position, 1, self.mode_combobox)
            elif key == "temperature":
                self.temperature_spinbox = QDoubleSpinBox()
                self.temperature_spinbox.setRange(0, 1)
                self.temperature_spinbox.setSingleStep(0.01)
                self.temperature_spinbox.setValue(value)
                self.temperature_spinbox.valueChanged.connect(self.update_temperature_value)
                self.input_table.setCellWidget(row_position, 1, self.temperature_spinbox)
            else:
                self.input_table.setItem(row_position, 1, QTableWidgetItem(str(value)))

    def update_model_value(self, value):
        self.step["ai"]["model"] = value
        self.step["ai"]["mode"] = 'chat'
        if value in ['text-curie-001', 'text-babbage-001', 'text-ada-001', 'text-davinci-003']:
            self.step["ai"]["mode"] = 'complete'
        self.mode_combobox.setCurrentText(str(self.step["ai"]["mode"]))
        self.log({'action': 'update_model_value', 'message': f"{self.process_name}::{self.step['name']}:{value}"})

    def update_models(self, models):
        self.model_keys = list(models.keys())
        self.model_combobox.clear()
        self.model_combobox.addItems(self.model_keys)
        self.model_combobox.setCurrentText(str(self.step["ai"]["model"]))

    def update_mode_value(self, value):
        self.step["ai"]["mode"] = value

    def update_temperature_value(self, value):
        self.step["ai"]["temperature"] = value

    def execute_selected_step(self):
        self.log({'action': 'execute_selected_step', 'message': f"{self.process_name}::{self.step['name']}"})
        SEND({'cmd': 'exec', 'object': 'step', 'cb': 'exec_step', 'record':
                {'process_name': self.process_name, 'step_name': self.step['name']}})



if __name__ == "__main__":
    app = QApplication([])
    step = {
        "name": "Step 1",
        "prompt_name": "Prompts/Flask/Use Case Description to Requirements.pe",
        "ai": {
            "model": "gpt-3.5-turbo",
            "temperature": 0,
            "max_tokens": 3000,
            "mode": "chat"
        },
        "storage_path": "Dynamic/Requirements",
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

    from PyQt5.QtWidgets import QMainWindow

    main_window = QMainWindow()
    display = InputTable("fTest Process", step)
    main_window.setCentralWidget(display)
    main_window.show()
    app.exec_()