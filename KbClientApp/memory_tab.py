from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QTreeView, QSplitter, QDirModel
from PyQt5.QtCore import Qt

from memory_model import MemoryModel
from log_tab import LOG


class MemoryTab(QWidget):
    MemoryStore = {}

    def log(self, message):
        message['system'] = 'memory_tab'
        LOG(message)

    def __init__(self, root_dir, parent):
        super().__init__(parent)
        self.selected_filename = None
        self.root_path = root_dir.split('/')
        self.layout = QVBoxLayout(self)
        self.splitter = QSplitter(Qt.Horizontal)
        self.tree = QTreeView(self.splitter)
        # self.model = QDirModel()
        # self.tree.setModel(self.model)
        self.model = MemoryModel(self.MemoryStore)
        self.tree.setModel(self.model)
        # self.tree.setRootIndex(self.model.index(root_dir))

        for i in range(1, 4):
            self.tree.hideColumn(i)

        self.edit = QTextEdit(self.splitter)
        self.layout.addWidget(self.splitter)
        self.tree.clicked.connect(self.select_file)

    # def select_file(self, index):
    #     full_file_name = self.model.filePath(index)
    #     full_path = full_file_name.split('/')
    #     root_path = full_path[len(self.root_path):]  # Skip all till 'Memory'
    #     self.selected_filename = '/'.join(root_path)
    #     ele = self.MemoryStore
    #     for i in root_path:
    #         ele = ele[i]
    #     self.edit.setText(ele)

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
        self.edit.setText(str(index.internalPointer().value))

    def memory_update(self, obj):
        # self.log({'action': 'memory_update', 'message': obj})
        data = obj['data']
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
        self.MemoryStore = obj['data']
        self.model.update(self.MemoryStore)

