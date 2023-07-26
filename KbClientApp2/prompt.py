from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QPushButton
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import json

from websocket import REGISTER_CALLBACK
from log_tab import LOG


class Prompt(QWidget):
    PromptStore = {}        # MemoryStorage of all prompts

    def __init__(self, parent):
        super().__init__()
        self.selected_item = None
        self.tree = None
        self.model = None
        self.parent = parent
        self.init_ui()
        REGISTER_CALLBACK(self, "memory_initial_load")
        REGISTER_CALLBACK(self, "memory_update")

    def load_data(self, parent, data):
        for key, value in data.items():
            item = QStandardItem(str(key))
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            parent.appendRow(item)
            if isinstance(value, dict):
                self.load_data(item, value)

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a QStandardItemModel
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Prompt Memory'])

        # self.load_data(model, {})

        # Create a QTreeView and set its model
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.selectionModel().selectionChanged.connect(self.item_selected)
        layout.addWidget(self.tree)

    def get_value(self, full_path):
        path = full_path.split('/')
        ele = self.PromptStore
        for idx in path:
            ele = ele[idx]
        return ele

    def item_selected(self, selected, deselected):
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]

            # Get the full path
            path = []
            while index.isValid():
                path.insert(0, self.model.data(index))
                index = index.parent()

            full_name = '/'.join(path)
            self.select_prompt(full_name)

    def select_prompt(self, full_name):
        self.selected_item = full_name
        value = self.get_value(self.selected_item)
        if isinstance(value, dict):
            return
        # print(f'{self.selected_item}:{value}')
        self.parent.prompt_editor.file_selected(self.selected_item, value)

    def log(self, msg):
        msg['system'] = 'Prompt'
        LOG(msg)

    def memory_initial_load(self, obj):
        self.log({'action': 'memory_initial_load', 'message': 'In Prompt::memory_initial_load'})
        self.PromptStore = obj['record']
        self.load_data(self.model, self.PromptStore)

    def memory_update(self, obj):
        data = obj['record']
        ele = self.PromptStore
        for key in data['path']:
            ele = ele[key]
        ele[data['name']] = data['content']
        self.log({'action': 'memory_update', 'message': f'In Prompt::memory_update({obj})'})
        if self.selected_item == '/'.join(data['path'])+'/'+data['name']:
            self.select_prompt(self.selected_item)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    window = Prompt(None)
    window.show()

    sys.exit(app.exec_())
