from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QColor


class OutputTable(QWidget):

    def __init__(self, step, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        # Output Table
        self.output_table = QTableWidget()
        self.output_table.setColumnCount(2)
        self.output_table.setHorizontalHeaderLabels(["Attribute", "Value"])
        self.output_table.horizontalHeader().setStretchLastSection(True)
        self.output_table.horizontalHeader().setStyleSheet("::section { background-color: #ADD8E6 }")  # Setting color
        self.layout.addWidget(self.output_table)

        for key, value in step.items():
            if key not in ["name", "prompt_name", "ai", "storage_path"]:
                row_position = self.output_table.rowCount()
                self.output_table.insertRow(row_position)
                self.output_table.setItem(row_position, 0, QTableWidgetItem(key))
                self.output_table.setItem(row_position, 1, QTableWidgetItem(str(value)))

    def update_step(self, process_name: str, new_step):
        # Clear the existing table
        self.output_table.setRowCount(0)

        # Update the step
        self.step = new_step

        # Update the table
        self._fill_output_table()

    def _fill_output_table(self):
        # Fill the output table with the new step
        for key, value in self.step.items():
            if key not in ["name", "prompt_name", "ai", "storage_path"]:
                row_position = self.output_table.rowCount()
                self.output_table.insertRow(row_position)
                self.output_table.setItem(row_position, 0, QTableWidgetItem(key))
                self.output_table.setItem(row_position, 1, QTableWidgetItem(str(value)))

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

    display = OutputTable(step)
    display.show()
    app.exec_()
