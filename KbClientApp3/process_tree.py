from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QApplication, QMenu, QInputDialog
from PySide6.QtGui import QIcon, QMouseEvent
from PySide6.QtCore import Qt
import json
import copy

from websocket import REGISTER_CALLBACK, SEND
from log_tab import LOG


class ProcessTree(QTreeWidget):
    def __init__(self, workbench, parent=None):
        super(ProcessTree, self).__init__(parent)
        self.workbench = workbench
        self.process_list = None
        self.selected_process_name = None
        self.selected_step_index = None
        self.setHeaderLabels(["Process/Steps", "Prompt Name"])
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.process_icon = QIcon("process-icon.png")  # Replace with the path to your process icon
        self.step_icon = QIcon("step-icon.png")  # Replace with the path to your step icon
        self.setColumnWidth(0, 300)  # Set a fixed width for the "Process/Steps" column
        REGISTER_CALLBACK(self, method_list=['process_list_initial_load'])

    def process_list_initial_load(self, message):
        self.log('process_list_initial_load', 'in Process::process_list_initial_load')
        # Clear existing items in the tree
        self.load_tree(message['record'])

    def log(self, action, message):
        LOG({'system': 'ProcessTree', 'action': action, 'message': message})

    def load_tree(self, process_dict):
        self.process_list = copy.deepcopy(process_dict)
        self.update_tree()

    def update_tree(self):
        self.clear()
        for process_name, steps in self.process_list.items():
            process_item = QTreeWidgetItem(self, [process_name])
            process_item.setIcon(0, self.process_icon)
            for step in steps:
                step_item = QTreeWidgetItem(process_item, [step['name'], step['prompt_name']])
                step_item.setIcon(0, self.step_icon)
        # self.expandAll()
        self.collapseAll()

    def get_item(self, item):
        parent = item.parent()
        if parent is not None:
            return parent.text(0), parent.indexOfChild(item)
        else:
            return item.text(0), None

    def update_selected(self):
        item = self.currentItem()
        if item is not None:
            self.selected_process_name, self.selected_step_index = self.get_item(item)
            self.log('update_selected', f'Selected {self.selected_process_name}::{self.selected_step_index}')
            if self.selected_step_index is not None:
                step = self.process_list[self.selected_process_name][self.selected_step_index]
                self.workbench.step_editor.set_step(self.selected_process_name, step)


    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.update_selected()

    def contextMenuEvent(self, event):
        # self.log('contextMenuEvent', f'yep it is called contextMenuEvent({event})')
        item = self.currentItem()
        if item is not None:
            self.setCurrentItem(item)
            self.update_selected()
            menu = QMenu(self)

            process_name, index = self.get_item(item)
            if index is None:  # It's a process
                delete_action = menu.addAction(f"Delete Process '{process_name}'")

            else:  # It's a step
                delete_action = menu.addAction(f"Delete Step '{item.text(0)}'")

            delete_action.triggered.connect(self.delete_process)

            add_step_action = menu.addAction("Step New")
            add_step_action.triggered.connect(self.create_step)

            add_process_action = menu.addAction("Create New Process")
            add_process_action.triggered.connect(self.create_process)

            exec_process_action = menu.addAction(f"Execute {process_name}")
            exec_process_action.triggered.connect(self.exec_process)

            menu.exec_(event.globalPos())

    def delete_process(self):
        item = self.currentItem()
        if item is not None:
            process_name, index = self.get_item(item)
            if index is None:  # It's a process
                record = {'process_name': process_name}
                msg = {'cmd': 'delete', 'object': 'process', 'cb': 'cb_delete_process', 'record': record }
            else:  # It's a step
                step = self.process_list[process_name][index]
                record = {'process_name': process_name, 'step_name': step['name']}
                msg = {'cmd': 'delete', 'object': 'step', 'cb': 'cb_delete_step', 'record': record }
            SEND(msg)

    def cb_delete_process(self, msg):
        process_name = msg['record']['process_name']
        if msg['rc'] == 'Okay':
            self.log('cb_delete_process', f"cb_delete_process({process_name}) completed successfully")
        else:
            self.log('cb_delete_process', f"Error: cb_delete_process({process_name}) reason: {msg['reason']}")

    def cb_delete_step(self, msg):
        process_name = msg['record']['process_name']
        step_name = msg['record']['step_name']
        if msg['rc'] == 'Okay':
            self.log('cb_delete_step', f"cb_delete_step({process_name},{step_name}) completed successfully")
        else:
            self.log('cb_delete_step', f"Error: cb_delete_step({process_name},{step_name}) reason: {msg['reason']}")

    def create_step(self):
        item = self.currentItem()
        if item is not None:
            process_name, index = self.get_item(item)
            if index is None:
                index = 0
            text, ok = QInputDialog.getText(self, "Step Name", "Enter Step Name:")
            if ok:
                record = {'process_name': process_name, 'step_index': index, 'step_name': text}
                SEND({'cmd': 'create', 'cb': 'cb_create_step', 'object': 'step', 'record': record})
                self.log("create_step", f"call create Process({text})")

                # self.process_list[process_name].append({"name": text, "prompt_name": ""})
                # self.update_tree()

    def cb_create_step(self, msg):
        if msg['rc'] == 'Okay':
            self.log('cb_create_step', f"Step {msg['record']['process_name']}::{msg['record']['step_name']} Created")
        else:
            self.log('cb_create_step',
                     f"Create Step {msg['record']['process_name']}::{msg['record']['step_name']} failed reason: {msg['reason']}")

    def create_process(self):
        text, ok = QInputDialog.getText(self, "Process Name", "Enter Process Name:")
        if ok:
            # The user clicked "OK" and provided a valid input
            record = {'process_name': text}
            SEND({'cmd': 'create', 'cb': 'cb_create_process', 'object': 'process', 'record': record})
            self.log("create_process", f"call create Process({text})")

    def cb_create_process(self, msg):
        if msg['rc'] == 'Okay':
            self.log('cb_create_process', f"Process {msg['record']['process_name']} Created")
        else:
            self.log('cb_create_process',
                     f"Create Process {msg['record']['process_name']} failed reason: {msg['reason']}")

    def exec_process(self):
        record = {'process_name': self.selected_process_name}
        SEND({'cmd': 'exec', 'cb': 'cb_exec_process', 'object': 'process', 'record': record})
        self.log("exec_process", f"call exec Process({self.selected_process_name})")

    def cb_exec_process(self, msg):
        if msg['rc'] == 'Okay':
            self.log('cb_exec_process', f"Process {msg['record']['process_name']} Created")
        else:
            self.log('cb_exec_process',
                     f"Execute Process {msg['record']['process_name']} failed reason: {msg['reason']}")

    def rename_process(self):
        self.process_list["New Process"] = []
        self.update_tree()

    def dropEvent(self, event):
        source_item = self.currentItem()
        target_item = self.itemAt(event.pos())
        if source_item is None or target_item is None or source_item == target_item:
            return

        from_process, from_step_no = self.get_item(source_item)
        to_process, to_step_no = self.get_item(target_item)

        if from_step_no is None:
            # Try to drag a Process
            return
        if to_step_no is None:
            # Drop on Directory, add as last element
            to_step_no = self.process_list[to_process].len()

        record = {'from_process': from_process, 'from_step_no': from_step_no,
                  'to_process': to_process, 'to_step_no': to_step_no}

        msg = {'cmd': 'move', 'object': 'step', 'cb': 'cb_move_step', 'record': record}
        SEND(msg)

    def cb_move_step(self, msg):
        if msg['rc'] == 'Okay':
            self.log('cb_move_step', f"Step moved ")
        else:
            self.log('cb_move_step', f"Move failed reason: {msg['reason']}")

    def process_step_update(self, msg):
        process_name = msg['object']
        step = msg['record']
        step_name = step['name']
        if msg['rc'] == 'Fail':
            self.log('process_step_update',
                     f"Error: Processing {process_name} Step {step_name} reason: {msg['reason']}...")
            return
        for idx, step in enumerate(self.process_list[process_name]):
            if step['name'] == step_name:
                self.process_list[process_name][idx] = step
        self.workbench.step_log.step_update(step)





if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    with open('ProcessList.json', 'r') as file:
        process_list = json.load(file)

    tree = ProcessTree()
    tree.load_tree(process_list)
    tree.show()

    sys.exit(app.exec())
