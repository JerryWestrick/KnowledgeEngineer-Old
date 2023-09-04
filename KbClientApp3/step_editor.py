from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QWidget, QFormLayout, QLabel, QLineEdit, QComboBox, QDoubleSpinBox, \
    QSpinBox, QPushButton, QHBoxLayout, QGroupBox, QTabWidget, QVBoxLayout, QTextEdit, QCheckBox, QTableWidget, \
    QTableWidgetItem, QMenu
from PySide6.QtCore import Qt

from websocket import REGISTER_CALLBACK, SEND
from log_tab import LOG


class MacrosWidget(QTableWidget):
    def __init__(self):
        super().__init__()

        # Initial setup
        self.macros: dict[str, str] = {}
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(['Macro', 'Value'])
        self.setRowCount(0)
        # self.populate_macros(macros)

        # Connect signals
        self.cellChanged.connect(self.on_cell_changed)

    def populate_macros(self, macros: dict[str, str]):
        self.setRowCount(0)  # Reset table
        self.macros = macros
        for row, key in enumerate(sorted(macros.keys())):
            value = macros[key]
            self.insertRow(row)
            self.setItem(row, 0, QTableWidgetItem(key))
            self.setItem(row, 1, QTableWidgetItem(value))

    def on_cell_changed(self, row, column):
        key_item = self.item(row, 0)
        value_item = self.item(row, 1)

        # Check if either key or value is None (i.e., the row is not fully populated)
        if not key_item or not value_item:
            return

        key = key_item.text()
        value = value_item.text()

        # Update your dictionary or do other processing as needed
        self.macros[key] = value

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        add_row_action = QAction('Add Row', self)
        delete_row_action = QAction('Delete Row', self)

        add_row_action.triggered.connect(self.add_row)
        delete_row_action.triggered.connect(self.delete_row)

        context_menu.addAction(add_row_action)
        context_menu.addAction(delete_row_action)

        # Show the context menu at the position of the mouse click
        context_menu.exec(event.globalPos())

    # Slot to handle adding a row
    def add_row(self):
        row_count = self.rowCount()
        self.insertRow(row_count)

    # Slot to handle deleting a row
    def delete_row(self):
        # Check if an entire row is selected
        selected_rows = self.selectionModel().selectedRows()
        if selected_rows:
            for index in reversed(selected_rows):
                self.removeRow(index.row())
            return

        # If not, check if a cell is selected
        selected_indexes = self.selectionModel().selectedIndexes()
        if selected_indexes:
            # Only take the row of the first selected cell (in case of multi-selection)
            row_to_remove = selected_indexes[0].row()
            self.removeRow(row_to_remove)


class StepEditor(QWidget):
    def __init__(self, workbench=None):
        super().__init__()
        self.step_name = None
        self.step = None
        self.process_name = None
        self.workbench = workbench
        self.models = {'gpt-3.5-turbo': {}, 'gpt-3.5-turbo-16k': {}, 'gpt-4': {}}

        # General Layout
        self.layout = QFormLayout(self)

        # General Step Parameters
        self.name_editor = QLineEdit()
        self.layout.addRow("Name:", self.name_editor)
        self.prompt_name_editor = QLineEdit()
        self.layout.addRow("Prompt Name:", self.prompt_name_editor)
        self.verify_prompt_editor = QLineEdit()
        self.layout.addRow("Verify Prompt:", self.verify_prompt_editor)
        self.storage_path_editor = QLineEdit()
        self.layout.addRow("Storage Path:", self.storage_path_editor)
        self.text_file_editor = QLineEdit()
        self.layout.addRow("Text File:", self.text_file_editor)

        # An AI Step:
        self.ai_call_tab = QTabWidget()
        self.ai_call_widget = QWidget()
        self.ai_call_layout = QFormLayout(self.ai_call_widget)

        self.model_editor = QComboBox()
        self.ai_call_layout.addRow("LLM Model:", self.model_editor)

        self.mode_editor = QComboBox()
        self.mode_editor.addItems(['chat', 'complete'])
        self.ai_call_layout.addRow("Mode:", self.mode_editor)

        self.temperature_editor = QDoubleSpinBox()
        self.ai_call_layout.addRow("Temperature:", self.temperature_editor)
        self.max_tokens_editor = QLineEdit()
        self.ai_call_layout.addRow("Max Tokens:", self.max_tokens_editor)
        self.ai_call_tab.addTab(self.ai_call_widget, "AI Call")

        # Code for the "For Each File" tab
        # ================================

        self.for_each_file_widget = QWidget()
        self.for_each_file_layout = QFormLayout(self.for_each_file_widget)

        self.file_process_enabled = QCheckBox("In the Following Process Generate a Step For Each File Matching", self)
        self.for_each_file_layout.addRow('Enable:', self.file_process_enabled)
        self.file_process_name = QLineEdit()
        self.for_each_file_layout.addRow('Process:', self.file_process_name)
        self.file_glob = QLineEdit()
        self.for_each_file_layout.addRow('Matching:', self.file_glob)
        self.file_glob_test_button = QPushButton('Test File Glob')
        self.for_each_file_layout.addRow('', self.file_glob_test_button)
        self.file_glob_list = QTextEdit()
        self.for_each_file_layout.addRow('Results:', self.file_glob_list)

        self.ai_call_tab.addTab(self.for_each_file_widget, "For Each File")

        # Code for the "Macros" tab
        # =========================

        self.macro_editor = MacrosWidget()
        macro_layout = QVBoxLayout(self.macro_editor)
        self.ai_call_tab.addTab(self.macro_editor, "Macro Editor")
        self.layout.addRow("Type Of Step:", self.ai_call_tab)

        # and the Save / Execute Step buttons
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

    def add_row(self):
        row_position = self.macro_editor.rowCount()
        self.macro_editor.insertRow(row_position)

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
        self.verify_prompt_editor.setText(self.step["verify_prompt"])
        self.text_file_editor.setText(self.step["text_file"])
        self.storage_path_editor.setText(self.step["storage_path"])
        self.temperature_editor.setValue(float(self.step["ai"]["temperature"]))
        self.max_tokens_editor.setText(str(self.step["ai"]["max_tokens"]))
        self.model_editor.setCurrentText(self.step["ai"]["model"])
        self.mode_editor.setCurrentText(self.step["ai"]["mode"])

        self.file_process_enabled.setChecked(self.step["file_process_enabled"])
        self.file_process_name.setText(self.step["file_process_name"])
        self.file_glob.setText(self.step["file_glob"])

        self.macro_editor.populate_macros(self.step['macros'])

        self.save_button.setText(f'Save {self.step["name"]}')
        self.execute_button.setText(f'Execute {self.step["name"]}')
        if self.workbench is not None and self.step['prompt_name'] != '':
            self.workbench.prompt_tree.set_prompt(self.step["prompt_name"])
            self.workbench.prompt_tree.set_prompt(step['prompt_name'])
            self.workbench.step_log.update_step({'record': step})  # fake msg

    def set_prompt_name(self, name):
        self.step['prompt_name'] = name
        self.prompt_name_editor.setText(self.step['prompt_name'])

    def set_storage_path(self, name):
        self.step['storage_path'] = name
        self.storage_path_editor.setText(self.step['storage_path'])

    def save_button_enable(self):
        self.save_button.setEnabled(True)

    def connect_signals(self):
        # Connect form field signals to enable the save button
        self.name_editor.textChanged.connect(self.save_button_enable)
        self.prompt_name_editor.textChanged.connect(self.save_button_enable)
        self.prompt_name_editor.textChanged.connect(self.save_button_enable)
        self.text_file_editor.textChanged.connect(self.save_button_enable)
        self.temperature_editor.valueChanged.connect(self.save_button_enable)
        self.max_tokens_editor.textChanged.connect(self.save_button_enable)
        self.model_editor.currentTextChanged.connect(self.save_button_enable)
        self.mode_editor.currentTextChanged.connect(self.save_button_enable)
        self.storage_path_editor.textChanged.connect(self.save_button_enable)

        # Connect button signals to their actions
        self.file_glob_test_button.clicked.connect(self.test_file_glob)
        self.save_button.clicked.connect(self.save_step)
        self.execute_button.clicked.connect(self.execute_step)

    def save_step(self):
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

    def test_file_glob(self):
        # Print the process name and step name
        self.log('test_file_glob', f'test_file_glob "{self.step["file_glob"]}"')
        msg = {"cmd": "test",
               "object": "file_glob",
               "cb": "cb_test_file_glob",
               "record": {"file_glob": self.file_glob.text()}
               }
        self.file_glob_test_button.setEnabled(False)
        SEND(msg)

    def cb_test_file_glob(self, msg):
        if msg['rc'] == 'Fail':
            self.log("cb_test_file_glob",
                     f"Error: Execution of File Glob '{msg['record']['file_glob']}' failed reason: {msg['reason']}")
        else:
            self.log("cb_test_file_glob", f"Execution of File Glob {msg['record']['file_glob']} confirmed")
        self.file_glob_list.setText('\n'.join(msg['record']['files']))
        self.file_glob_test_button.setEnabled(True)

    def get_step(self):
        self.step["name"] = self.name_editor.text()
        self.step["prompt_name"] = self.prompt_name_editor.text()
        self.step["verify_prompt"] = self.verify_prompt_editor.text()
        self.step["text_file"] = self.text_file_editor.text()
        self.step["storage_path"] = self.storage_path_editor.text()
        self.step["file_process_enabled"] = self.file_process_enabled.isChecked()
        self.step["file_process_name"] = self.file_process_name.text()
        self.step["file_glob"] = self.file_glob.text()
        self.step["macros"] = self.macro_editor.macros
        self.step["ai"]["temperature"] = self.temperature_editor.value()
        self.step["ai"]["max_tokens"] = int(self.max_tokens_editor.text())
        self.step["ai"]["model"] = self.model_editor.currentText()
        self.step["ai"]["mode"] = self.mode_editor.currentText()
        return self.step


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    step = {
        "py/object": "KbServerApp.step.Step",
        "name": "Step 1",
        "prompt_name": "Prompts/Test Prompt.pe",
        "verify_prompt": "Prompts/Test Prompt.pe",
        "storage_path": "Dynamic/Requirements",
        "text_file": "test text File",
        "file_process_enabled": True,
        "file_process_name": "Test Process name",
        "file_glob": "Snake/Dynamic/Server/Step*.md",
        "macros": {"version": "1.0", "filename": "Step_01.md"},
        "ai": {
            "py/object": "KbServerApp.ai.AI",
            "temperature": 0.0,
            "max_tokens": 3000,
            "model": "gpt-3.5-turbo-16k",
            "mode": "chat",
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
    }

    editor = StepEditor()
    editor.set_step("MyProcess", step)
    editor.show()

    sys.exit(app.exec())
