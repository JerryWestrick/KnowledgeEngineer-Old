from PyQt5.QtCore import Qt

from log_tab import LogTab
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QHBoxLayout, QSplitter, QGroupBox, \
    QPushButton

from step_input import InputTable
from step_output import OutputTable
from log_tab import LOG
from websocket import SEND


class ProcessTab(QWidget):
    ModelsStore: dict = {}
    ProcessStore: dict = {}
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

    def log(self, message):
        message['system'] = 'process'
        LOG(message)

    def __init__(self, parent):

        super().__init__()
        self.parent = parent
        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Process", "Step Name"])

        self.process_name = ''
        self.steps = None
        self.step = self.empty_step
        self.input_display = InputTable("", self.empty_step, self)

        # Create the button
        self.execute_button = QPushButton("Execute Process")

        # Connect the button to the function that executes the process
        self.execute_button.clicked.connect(self.execute_selected_process)

        # Create a QVBoxLayout, add the tree widget and the button to it
        vbox = QVBoxLayout()
        vbox.addWidget(self.tree)
        vbox.addWidget(self.execute_button)

        # Create a QWidget, set the QVBoxLayout as its layout
        widget = QWidget()
        widget.setLayout(vbox)

        self.hsplitter = QSplitter(Qt.Horizontal)
        self.hsplitter.addWidget(widget)

        self.hsplitter.addWidget(self.input_display)
        self.hsplitter.setSizes([1, 3])

        self.output_display = OutputTable(self.empty_step, self)

        self.vsplitter = QSplitter(Qt.Vertical)
        self.vsplitter.addWidget(self.hsplitter)
        self.vsplitter.addWidget(self.output_display)
        self.vsplitter.setSizes([1, 3])

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.vsplitter)
        self.setLayout(self.layout)

        # Connect the itemClicked signal to the on_item_clicked slot
        self.tree.itemClicked.connect(self.on_item_clicked)

    def execute_selected_process(self):
        self.log({'action': 'execute_selected_process', 'message': self.process_name})
        SEND({'cmd': 'exec', 'object': 'process', 'cb': 'exec_process_log', 'record': {'process': self.process_name}})


    def on_item_clicked(self, item, column):
        process_name = item.parent().text(0) if item.parent() is not None else None
        step_name = item.text(1) if column == 1 else None

        if process_name and step_name:
            self.process_name = process_name
            self.execute_button.setText(f"Execute Process {self.process_name}")
            steps = self.ProcessStore[process_name]
            for step in steps:
                if step['name'] == step_name:
                    self.input_display.update_step(self.process_name, step)
                    self.output_display.update_step(self.process_name, step)
                    break

    def load_data(self):
        self.tree.clear()  # Clear the tree before loading new data
        pname = None
        for process, steps in self.ProcessStore.items():
            if self.process_name == '':
                self.process_name = process
            parent = QTreeWidgetItem(self.tree)
            parent.setText(0, process)
            for step in steps:
                child = QTreeWidgetItem(parent)
                child.setText(1, step['name'])
        self.steps = self.ProcessStore[self.process_name]
        self.step = self.steps[0]


    def process_step_update(self, obj):
        self.log({'action': 'process_step_update', 'message': obj})
        process_name = obj['object']
        new_step = obj['data']
        step_name = new_step['name']
        this_process = self.ProcessStore[process_name]
        for index, step in enumerate(this_process):
            if step['name'] == step_name:
                this_process[index] = new_step
                break

        if process_name == self.process_name and step_name == self.step['name']:
            self.step = new_step
            self.input_display.update_step(self.process_name, new_step)
            self.output_display.update_step(self.process_name, new_step)

    def process_list_initial_load(self, obj):
        self.log({'action': 'process_list_initial_load', 'message': obj})
        self.ProcessStore = obj
        self.load_data()

    def models_initial_load(self, obj):
        self.log({'action': 'models_initial_load', 'message': obj})
        self.ModelsStore = obj['data']
        self.input_display.update_models(self.ModelsStore)



