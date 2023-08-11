from PySide6.QtWidgets import QApplication, QWidget, QFormLayout, QLabel, QLineEdit, QComboBox, QDoubleSpinBox, \
    QSpinBox, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt

from websocket import REGISTER_CALLBACK, SEND
from log_tab import LOG


class StepEditor(QWidget):
    def __init__(self, workbench=None):
        super().__init__()
        self.step_name = None
        self.step = None
        self.process_name = None
        self.workbench = workbench
        self.models = {'gpt-3.5-turbo': {}, 'gpt-3.5-turbo-16k': {}, 'gpt-4': {}}
        self.layout = QFormLayout(self)

        self.name_editor = QLineEdit()
        self.layout.addRow("Name:", self.name_editor)

        self.prompt_name_editor = QLineEdit()
        self.layout.addRow("Prompt Name:", self.prompt_name_editor)

        self.storage_path_editor = QLineEdit()
        self.layout.addRow("Storage Path:", self.storage_path_editor)

        self.text_file_editor = QLineEdit()
        self.layout.addRow("Text File:", self.text_file_editor)

        self.model_editor = QComboBox()
        # self.model_editor.addItems(self.models.keys())
        self.layout.addRow("Model:", self.model_editor)

        self.mode_editor = QComboBox()
        self.mode_editor.addItems(['chat', 'complete'])
        self.layout.addRow("Mode:", self.mode_editor)

        self.temperature_editor = QDoubleSpinBox()
        self.temperature_editor.setRange(0, 1)
        self.layout.addRow("Temperature:", self.temperature_editor)

        self.max_tokens_editor = QLineEdit()
        self.layout.addRow("Max Tokens:", self.max_tokens_editor)

        button_layout = QHBoxLayout()
        self.save_button = QPushButton('Save')
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)

        button_layout.addStretch()

        self.execute_button = QPushButton('Execute')
        button_layout.addWidget(self.execute_button)

        self.layout.addRow(button_layout)
        self.connect_signals()
        REGISTER_CALLBACK(self, method_list=['models_initial_load'])

    def log(self, action, message):
        LOG({'system': 'StepEditor', 'action': action, 'message': message})

    def models_initial_load(self, msg):
        self.log('models_initial_load', f'models_initial_load({msg})')
        self.models = msg['record']
        self.model_editor.addItems(self.models.keys())

    def set_step(self, process_name, step):
        self.log('set_step', f'set_step({process_name}, {step})')
        self.process_name = process_name
        self.step_name = step['name']
        self.step = step

        self.name_editor.setText(self.step["name"])
        self.prompt_name_editor.setText(self.step["prompt_name"])
        self.text_file_editor.setText(self.step["text_file"])
        self.temperature_editor.setValue(float(self.step["ai"]["temperature"]))
        self.max_tokens_editor.setText(str(self.step["ai"]["max_tokens"]))
        self.model_editor.setCurrentText(self.step["ai"]["model"])
        self.mode_editor.setCurrentText(self.step["ai"]["mode"])
        self.storage_path_editor.setText(self.step["storage_path"])

        self.save_button.setText(f'Save {self.step["name"]}')
        self.execute_button.setText(f'Execute {self.step["name"]}')
        if self.step['prompt_name'] != '':
            self.workbench.prompt_tree.set_prompt(self.step["prompt_name"])
            self.workbench.prompt_tree.set_prompt(step['prompt_name'])
            self.workbench.step_log.update_step({'record': step})  # fake msg

    def set_prompt_name(self, name):
        self.step['prompt_name'] = name
        self.prompt_name_editor.setText(self.step['prompt_name'])

    def set_storage_path(self, name):
        self.step['storage_path'] = name
        self.storage_path_editor.setText(self.step['storage_path'])

    def connect_signals(self):
        # Connect form field signals to enable the save button
        self.name_editor.textChanged.connect(lambda: self.save_button.setEnabled(True))
        self.prompt_name_editor.textChanged.connect(lambda: self.save_button.setEnabled(True))
        self.text_file_editor.textChanged.connect(lambda: self.save_button.setEnabled(True))
        self.temperature_editor.valueChanged.connect(lambda: self.save_button.setEnabled(True))
        self.max_tokens_editor.textChanged.connect(lambda: self.save_button.setEnabled(True))
        self.model_editor.currentTextChanged.connect(lambda: self.save_button.setEnabled(True))
        self.mode_editor.currentTextChanged.connect(lambda: self.save_button.setEnabled(True))
        self.storage_path_editor.textChanged.connect(lambda: self.save_button.setEnabled(True))

        # Connect button signals to their actions
        self.save_button.clicked.connect(self.save_step)
        self.execute_button.clicked.connect(self.execute_step)

    def save_step(self):
        # This is where you should implement saving the step
        # For now, it just disables the save button and prints a message
        self.save_button.setEnabled(False)
        self.log('save_step', f'Saved step: {self.get_step()}')
        msg = {"cmd": "write", "object": "step", "cb": "cb_write_step",
               "record": {"process_name": self.process_name,
                          "step_name": self.step_name,
                          "step": self.get_step()
                          }
               }
        SEND(msg)

    def cb_write_step(self, msg):
        self.save_button.setEnabled(True)
        if msg['rc'] != 'Fail':
            self.log('cb_write_step', 'Received confirmation of Step Write')
        else:
            self.log('cb_write_step', f'Error: Step Write Failed Reason: {msg["reason"]}')

    def execute_step(self):
        # Print the process name and step name
        self.log('execute_step', f'Executing step "{self.step["name"]}" in process "{self.process_name}"')
        msg = {"cmd": "exec",
               "object": "step",
               "cb": "cb_exec_step",
               "record": {"process_name": self.process_name, "step_name": self.step_name}}
        self.execute_button.setEnabled(False)
        SEND(msg)

    def cb_exec_step(self, msg):
        if msg['rc'] == 'Fail':
            self.log("cb_exec_step", f"Error: Execution of Step {self.step_name} failed reason: {msg['reason']}")
        else:
            self.log("cb_exec_step", f"Execution of Step {self.step_name} confirmed")
        self.execute_button.setEnabled(True)

    def get_step(self):
        self.step["name"] = self.name_editor.text()
        self.step["prompt_name"] = self.prompt_name_editor.text()
        self.step["text_file"] = self.text_file_editor.text()
        self.step["ai"]["temperature"] = self.temperature_editor.value()
        self.step["ai"]["max_tokens"] = int(self.max_tokens_editor.text())
        self.step["ai"]["model"] = self.model_editor.currentText()
        self.step["ai"]["mode"] = self.mode_editor.currentText()
        self.step["storage_path"] = self.storage_path_editor.text()
        return self.step


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    step = {
        "py/object": "KbServerApp.step.Step",
        "name": "Step 1",
        "prompt_name": "Prompts/Test Prompt.pe",
        "ai": {
            "py/object": "KbServerApp.ai.AI",
            "temperature": 0.0,
            "max_tokens": 3000,
            "model": "gpt-3.5-turbo-16k",
            "mode": "chat"
        },
        "storage_path": "Dynamic/Requirements",
        "text_file": "",
        "messages": [],
        "answer": "",
        "files": {},
        "e_stats": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "sp_cost": 0.0,
            "sc_cost": 0.0,
            "s_total": 0.0,
            "elapsed_time": 0.0
        }
    }

    editor = StepEditor()
    editor.set_step("MyProcess", step)
    editor.show()

    sys.exit(app.exec())
