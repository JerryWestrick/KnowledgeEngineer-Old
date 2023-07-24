from PyQt5.QtWidgets import QApplication, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QPushButton

from websocket import SEND
from log_tab import LOG


class InputTable(QWidget):

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
            self.input_table.setItem(row_position, 0, QTableWidgetItem(key))
            self.input_table.setItem(row_position, 1, QTableWidgetItem(str(self.step[key])))

        for key, value in self.step["ai"].items():
            row_position = self.input_table.rowCount()
            self.input_table.insertRow(row_position)
            self.input_table.setItem(row_position, 0, QTableWidgetItem(key))
            self.input_table.setItem(row_position, 1, QTableWidgetItem(str(value)))

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
