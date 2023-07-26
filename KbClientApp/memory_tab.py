from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QTreeView, QSplitter, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

from read_only_dialog import ReadOnlyDialog
from websocket import SEND
from memory_model import MemoryModel
from log_tab import LOG


class MemoryTab(QWidget):
    MemoryStore = {}

    def log(self, message):
        message['system'] = 'memory_tab'
        LOG(message)

    def __init__(self, parent):
        super().__init__(parent)
        self.selected_filename = None

        self.layout = QHBoxLayout(self)  # Changed from QVBoxLayout to QHBoxLayout
        self.tree = QTreeView()
        self.model = MemoryModel(self.MemoryStore)
        self.tree.setModel(self.model)

        for i in range(1, 4):
            self.tree.hideColumn(i)

        self.layout.addWidget(self.tree)
        self.tree.clicked.connect(self.select_file)

        self.right_layout = QVBoxLayout()  # New QVBoxLayout for the right side

        self.edit = QTextEdit()
        self.edit.textChanged.connect(self.handle_text_changed)
        self.right_layout.addWidget(self.edit)

        self.button_layout = QHBoxLayout()
        self.save_button = QPushButton('Save', self)
        self.save_button.clicked.connect(self.save_content)
        self.save_button.setDisabled(True)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addStretch()

        self.test_button = QPushButton('Test', self)
        self.test_button.clicked.connect(self.test_content)
        self.test_button.setDisabled(True)
        self.button_layout.addWidget(self.test_button)

        self.right_layout.addLayout(self.button_layout)
        self.layout.addLayout(self.right_layout)

    def handle_text_changed(self):
        new_text = self.edit.toPlainText()
        if self.selected_filename is not None and new_text != self.get_file_contents(self.selected_filename):
            self.save_button.setEnabled(True)
            self.test_button.setDisabled(True)
        else:
            self.save_button.setDisabled(True)
            self.test_button.setEnabled(True)

    def file_saved(self, obj):
        self.log({'action': 'file_saved', 'message': obj})
        self.save_button.setDisabled(True)
        self.test_button.setEnabled(True)
        # Add the code to save the content here.

    def save_content(self):

        # Add the code to save the content here.

        if self.selected_filename is not None:
            new_file_content = self.edit.toPlainText()
            self.MemoryStore[self.selected_filename] = new_file_content
            SEND({'cmd': 'write', 'object': self.selected_filename, 'cb': 'file_saved',
                  'record': {'text': new_file_content}})
            self.save_button.setDisabled(True)
            self.test_button.setDisabled(True)
        else:
            self.save_button.setDisabled(True)
            self.test_button.setEnabled(True)

    def test_content(self):
        # Add the code to test the content here.
        self.log({'action': 'test_content', 'message': self.edit.toPlainText()})
        self.test_button.setDisabled(True)
        SEND({'cmd': 'read', 'object': 'memory', 'cb': 'memory_test', 'record': {'prompt_name': self.selected_filename}})

    def memory_test(self, obj):
        # self.log({'action': 'memory_test', 'message': obj})
        prompt_name = obj['object']
        expanded_text = ''
        for line in obj['record']['text']:
            expanded_text += f"{line['role']}: {line['content']} \n"
        self.test_button.setEnabled(True)
        dialog = ReadOnlyDialog(prompt_name, expanded_text)
        dialog.exec_()

    def select_file(self, index):
        if not index.isValid():
            return

        node = index.internalPointer()
        if node.children:
            return  # This is a directory, not a file.

        # Traverse the tree from the current node up to the root to get the full path.
        path_parts = []
        while node is not None and node.key is not None:
            path_parts.append(node.key)
            node = node.parent

        # The path_parts list is in reverse order (from leaf to root), so reverse it.
        full_path = path_parts[::-1]

        self.selected_filename = '/'.join(full_path)
        text_1 = self.get_file_contents(self.selected_filename)
        text_2 = str(index.internalPointer().value)
        # self.log({'action': 'select_file', 'message': f'{self.selected_filename} - {text_1} - {text_2}'})
        self.edit.setText(str(index.internalPointer().value))
        self.handle_text_changed()

    def get_file_contents(self, filename):
        path = filename.split('/')
        ele = self.MemoryStore
        for i in path:
            ele = ele[i]
        return ele

    def memory_update(self, obj):
        # self.log({'action': 'memory_update', 'message': obj})
        data = obj['record']
        ele = self.MemoryStore
        for i in data['path']:
            ele = ele[i]
        filename = f'{"/".join(data["path"])}/{data["name"]}'
        if 'modify' in data['mask']:
            ele[data['name']] = data['content']
            self.log({'action': 'memory_update',
                      'message': f'Update MemoryStore: {filename}'})
            if self.selected_filename == filename:
                self.edit.setText(data['content'])

        elif 'create' in data['mask']:
            ele[data['name']] = data['content']
            self.log({'action': 'memory_update',
                      'message': f'Create MemoryStore: {filename}'})

        elif 'delete' in data['mask']:
            del ele[data['name']]
            self.log({'action': 'memory_update',
                      'message': f'Delete MemoryStore: {filename}'})

    def memory_initial_load(self, obj):
        self.log({'action': 'memory_initial_load', 'message': obj})
        self.MemoryStore = obj['record']
        self.model.update(self.MemoryStore)
