from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QPushButton, QTreeWidgetItem

from websocket import REGISTER_CALLBACK
from log_tab import LOG


class Process(QWidget):
    ProcessStore = {}

    def __init__(self, parent):
        super().__init__()
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

        layout.addWidget(self.tree)

        # Create an array of buttons
        buttons = ["Execute", "New", "Save", "Delete", "Reload"]

        # Create a QHBoxLayout for the buttons
        button_layout = QHBoxLayout()

        for button in buttons:
            button_layout.addWidget(QPushButton(button))

        # Add the button layout to the main layout
        layout.addLayout(button_layout)

        self.setWindowTitle('Process')
        self.show()

    def process_step_update(self, obj):
        process_name = obj['object']
        new_step = obj['data']
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
        self.ProcessStore = obj['data']

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
        process = process = item.parent()
        if process:
            self.selected_process = process.text(0)
            self.selected_step = item.text(0)
            # print(f"Step clicked : {self.selected_process}:{self.selected_step}")
            for step in self.ProcessStore[self.selected_process]:
                if step['name'] == self.selected_step:
                    self.sync_widgets_with_process(self.selected_process, step)

    def sync_widgets_with_process(self, process_name, step):

        if self.selected_process != process_name:
            print(f"sync with {process_name} but selected process is {self.selected_process} - ignoring")
            return

        if self.selected_step != step['name']:
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
