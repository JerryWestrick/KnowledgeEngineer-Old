from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QLabel, QVBoxLayout, QTextEdit, QSplitter

from output_editor import OutputEditor
from prompt_editor import PromptEditor
from prompt import Prompt
from step_output import OutputTable
from step_input import InputTable
from process import Process

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


class WorkbenchTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.process_widget = Process(self)
        self.input_table = InputTable("", empty_step, self)
        self.output_table = OutputTable(self)
        self.prompt_widget = Prompt(self)
        self.prompt_editor = PromptEditor(self)
        self.output_editor = OutputEditor(self)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        row1 = QSplitter(Qt.Horizontal)
        row1.addWidget(self.process_widget)
        row1.addWidget(self.input_table)
        layout.addWidget(row1)

        row2 = QSplitter(Qt.Horizontal)
        row2.addWidget(self.prompt_widget)
        row2.addWidget(self.prompt_editor)
        layout.addWidget(row2)

        row3 = QSplitter(Qt.Horizontal)
        row3.addWidget(self.output_table)
        row3.addWidget(self.output_editor)
        layout.addWidget(row3)

        self.setWindowTitle('Workbench Tab')
        self.show()


def main():
    app = QApplication([])
    ex = WorkbenchTab(None)
    app.exec_()


if __name__ == '__main__':
    main()
