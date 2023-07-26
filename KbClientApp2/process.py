from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QPushButton, QTreeWidgetItem, \
    QMenu

from rename_process import RenameProcessDialog
from websocket import SEND, REGISTER_CALLBACK
from log_tab import LOG

empty_step = {
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


class Process(QWidget):
    ProcessStore = {}

    def __init__(self, parent):
        super().__init__()
        self.selected_is_step = False
        self.selected_step = None
        self.selected_process = None
        self.tree = None
        self.parent = parent
        self.init_ui()
        REGISTER_CALLBACK(self, 'process_list_initial_load')
        REGISTER_CALLBACK(self, 'process_step_update')

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a QTreeWidget
        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Process/Step", "Prompt"])

        # Connect the itemClicked signal to a custom slot
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.on_tree_context_menu)

        layout.addWidget(self.tree)

        self.setWindowTitle('Process')
        self.show()

    def on_tree_context_menu(self, point):
        # This method is called when the user right-clicks an item in the tree.
        # Create a QMenu
        context_menu = QMenu(self)

        # Placeholder for actions
        add_step_action = None
        delete_step_action = None
        add_process_action = None
        rename_process_action = None
        execute_process_action = None
        execute_step_action = None
        add_first_step_action = None

        # Add actions to the context menu
        if self.selected_is_step:
            execute_step_action = context_menu.addAction(f"Execute {self.selected_step} from {self.selected_process}")
            add_step_action = context_menu.addAction(f"Add New Step After {self.selected_step}")
            delete_step_action = context_menu.addAction(f"Delete {self.selected_step} from {self.selected_process}")
        else:
            add_first_step_action = context_menu.addAction(f"Add First Step to {self.selected_process} Process")
            execute_process_action = context_menu.addAction(f"Execute {self.selected_process} Process")
            add_process_action = context_menu.addAction("Create a new Process")
            rename_process_action = context_menu.addAction(f"Rename {self.selected_process} Process")

        # Execute the context menu
        action = context_menu.exec_(self.tree.mapToGlobal(point))

        # @Todo: Handle Process Popup Menu Actions
        if add_step_action is not None and action == add_step_action:
            print(f"Add New Step After {self.selected_step} in process {self.selected_process}")
        elif add_first_step_action is not None and action == delete_step_action:
            print(f"Add First Step to {self.selected_process} Process")
        elif delete_step_action is not None and action == delete_step_action:
            print(f"Delete {self.selected_process}:{self.selected_step}")
        elif add_process_action is not None and action == add_process_action:
            print("Add New Process")
        elif rename_process_action is not None and action == rename_process_action:
            old_name = self.selected_process
            RenameProcessDialog(old_name, self).exec_()  # The Dialog directly updates self.selected_process
            self.log({'action': 'rename_process', 'message': f'Rename Process <{old_name}> to <{self.selected_process}>'})
            SEND({'cmd': 'rename', 'object': 'process', 'cb': 'process_renamed', 'record':
                 {'process_old_name': old_name, 'process_new_name': self.selected_process}})
        elif execute_process_action is not None and action == execute_process_action:
            self.log({'action': 'execute_selected_process', 'message': self.selected_process})
            SEND({'cmd': 'exec', 'object': 'process', 'cb': 'exec_process_log',
                  'record': {'process': self.selected_process}})
        elif execute_step_action is not None and action == execute_step_action:
            self.log({'action': 'execute_selected_step', 'message': f"{self.selected_process}::{self.selected_step}"})
            SEND({'cmd': 'exec', 'object': 'step', 'cb': 'exec_step', 'record':
                 {'process_name': self.selected_process, 'step_name': self.selected_step}})

    def process_step_update(self, obj):
        process_name = obj['object']
        new_step = obj['record']
        for idx, step in enumerate(self.ProcessStore[process_name]):
            if step['name'] == new_step['name']:
                self.ProcessStore[process_name][idx] = new_step
                break
        self.log({'action': 'process_step_update', 'message': f'in {process_name}::{step["name"]}'})
        self.sync_widgets_with_process(process_name, new_step)
        # self.parent.input_table.update_step(process_name, step)

    def process_list_initial_load(self, obj):
        self.log({'action': 'process_list_initial_load', 'message': 'in Process::process_list_initial_load'})
        # Clear existing items in the tree
        self.tree.clear()
        self.ProcessStore = obj['record']

        # Loop through data and populate QTreeWidget
        for key in self.ProcessStore:
            parent = QTreeWidgetItem(self.tree)
            parent.setText(0, key)
            for step in self.ProcessStore[key]:
                child = QTreeWidgetItem(parent)
                child.setText(0, step['name'])
                child.setText(1, step['prompt_name'])
        self.tree.expandAll()

    def on_tree_item_clicked(self, item, column):
        # This method will be called when an item in the QTreeWidget is clicked.
        # You can implement your handling logic here.
        process = item.parent()
        self.selected_is_step = False
        if process:  # Okay We clicked a Step...
            self.selected_is_step = True
            self.selected_process = process.text(0)
            self.selected_step = item.text(0)
            # print(f"Process clicked : {self.selected_process}")
            for step in self.ProcessStore[self.selected_process]:
                if step['name'] == self.selected_step:
                    self.sync_widgets_with_process(self.selected_process, step)
            self.selected_process = process.text(0)
            self.selected_step = item.text(0)
            # print(f"Step clicked : {self.selected_process}:{self.selected_step}")
            for step in self.ProcessStore[self.selected_process]:
                if step['name'] == self.selected_step:
                    self.sync_widgets_with_process(self.selected_process, step)
        else:  # Okay We Clicked a process
            self.selected_is_step = False
            self.selected_process = item.text(0)
            self.selected_step = empty_step['name']
            self.sync_widgets_with_process(self.selected_process, empty_step)

    def sync_widgets_with_process(self, process_name, step):

        if self.selected_process != process_name:
            print(f"sync with {process_name} but selected process is {self.selected_process} - ignoring")
            return

        if self.selected_step is not None and self.selected_step != step['name']:
            print(f"sync with {step['name']} but selected step is {self.selected_step} - ignoring")
            return

        self.parent.input_table.update_step(process_name, step)
        self.parent.output_table.update_step(process_name, step)
        self.parent.prompt_widget.select_prompt(step['prompt_name'])

    def log(self, msg):
        msg['system'] = 'Process'
        LOG(msg)


def main():
    app = QApplication([])
    ex = Process(None)
    app.exec_()


if __name__ == '__main__':
    main()
