import json
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy, \
    QTreeWidget, QTreeWidgetItem, QAbstractItemView, QMenu, QInputDialog

from log_tab import LOG
from websocket import REGISTER_CALLBACK, SEND


class DragDropTreeWidget(QTreeWidget):
    def __init__(self, parent=None):
        super(DragDropTreeWidget, self).__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)

    def dropEvent(self, event):
        # Item that started the drag.
        source_item = self.currentItem()
        # Use drop position to find target item.
        target_item = self.itemAt(event.pos())
        if source_item is not None and target_item is not None:
            self.parent().drag_n_drop(source_item, target_item)
        return

class PromptTree(QWidget):
    def __init__(self, workbench):
        self.data = None
        self.selected_file = None
        self.selected_directory = None
        self.workbench = workbench
        super().__init__()

        self.setWindowTitle("Tree Widget Example")

        # Create a vertical box layout
        layout = QVBoxLayout(self)

        # Create a horizontal box layout
        hbox = QHBoxLayout()

        # Create a label
        self.label = QLabel("Label")
        # Create a spacer
        spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        # Create a button
        self.button = QPushButton("")
        self.button.clicked.connect(self.set_step_storage_clicked)

        # Add the label, spacer, and button to the hbox layout
        hbox.addWidget(self.label)
        hbox.addSpacerItem(spacer)
        hbox.addWidget(self.button)

        # Create a tree widget
        self.tree_widget = DragDropTreeWidget()
        self.tree_widget.setColumnCount(1)
        self.tree_widget.setHeaderLabels(["Prompts and Memory"])
        self.tree_widget.itemClicked.connect(self.handle_click)

        # Add the hbox layout and tree widget to the vbox layout
        layout.addLayout(hbox)
        layout.addWidget(self.tree_widget)
        self.tree_widget.itemExpanded.connect(self.handle_expanded)
        self.tree_widget.itemCollapsed.connect(self.handle_collapsed)
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.on_context_menu)
        REGISTER_CALLBACK(self, method_list=['process_list_initial_load'])

    def log(self, action, message):
        LOG({'system': 'PromptTree', 'action': action, 'message': message})

    def handle_expanded(self, item):
        # This slot is called when an item is expanded.
        # Here, you can set the icon of the item to an open folder icon.
        path = self.get_index(item)
        ele = self.get_data(path)
        if type(ele) is dict:
            item.setIcon(0, QIcon('folder_open_icon2.png'))

    def handle_collapsed(self, item):
        # This slot is called when an item is collapsed.
        # Here, you can set the icon of the item to a closed folder icon.
        path = self.get_index(item)
        ele = self.get_data(path)
        if type(ele) is dict:
            item.setIcon(0, QIcon('folder_closed_icon2.png'))

    def drag_n_drop(self, source_item, target_item):
        from_path = self.get_index(source_item)

        # Am I moving a directory?
        from_data = self.get_data(from_path)
        is_dir = type(from_data) == dict

        from_name = from_path.pop()

        to_path = self.get_index(target_item)
        to_ele = self.get_data(to_path)

        # go back to last Directory
        if type(to_ele) is str:
            to_path.pop()
            to_ele = self.get_data(to_path)

        if is_dir:
            self.log('move_directory', f'move dir({from_name}) from dir:{from_path} to dir:{to_path}')
            self.move_directory(from_name, '/'.join(from_path), '/'.join(to_path))
        else:
            self.log('move_memory', f'move file({from_name}) from dir:{from_path} to dir:{to_path}')
            self.move_memory(from_name, '/'.join(from_path), '/'.join(to_path))

    def move_directory(self, name, from_path, to_path):
        record = {'prompt_name': name, 'from_path': from_path, 'to_path': to_path}
        SEND({'cmd': 'move', 'object': 'directory', 'cb': 'cb_move_directory', 'record': record})

    def cb_move_directory(self, msg):
        name = msg['record']['prompt_name']
        from_path = msg['record']['from_path']
        to_path = msg['record']['to_path']
        if msg['rc'] == 'Okay':
            self.log('cb_move_directory', f"cb_move_directory moved {name} from {from_path} to {to_path}")
        else:
            self.log('cb_move_directory', f"cb_move_directory failed reason: {msg['reason']}")

    def move_memory(self, name, from_path, to_path):
        record = {'prompt_name': name, 'from_path': from_path, 'to_path': to_path}
        SEND({'cmd': 'move', 'object': 'memory', 'cb': 'cb_move_memory', 'record': record})

    def cb_move_memory(self, msg):
        name = msg['record']['prompt_name']
        from_path = msg['record']['from_path']
        to_path = msg['record']['to_path']
        if msg['rc'] == 'Okay':
            self.log('cb_move_memory', f"cb_move_memory moved {name} from {from_path} to {to_path}")
        else:
            self.log('cb_move_memory', f"cb_move_memory failed reason: {msg['reason']}")

    def set_step_storage_clicked(self):
        self.log('set_step_storage_clicked', f'set_step_storage_clicked({self.selected_directory})')
        self.workbench.step_editor.set_storage_path(self.selected_directory)

    def set_prompt(self, full_path):
        self.selected_file = full_path
        path = full_path.split('/')
        current_item = self.tree_widget.invisibleRootItem()
        for component in path:
            for i in range(current_item.childCount()):
                child = current_item.child(i)
                if child.text(0) == component:
                    self.tree_widget.setCurrentItem(child)
                    self.tree_widget.expandItem(child)
                    current_item = child
                    break
        prompt = self.get_data(path)
        self.workbench.prompt_editor.set_prompt(full_path, prompt)
        self.log('PromptTree', f'file selected {full_path}')

    def handle_click(self, item, _):
        # Check if the item is a directory (has child items)
        path = self.get_index(item)
        full_path = '/'.join(path)
        element = self.get_data(path)
        if type(element) is dict:
            self.selected_directory = full_path
            self.button.setText(f"Set Step storage_path: {self.selected_directory}")
            self.label.setText(f"Directory: {self.selected_directory}")
        else:
            # Log the file selection
            self.selected_file = full_path
            self.workbench.prompt_editor.set_prompt(full_path, element)
            self.log('PromptTree', f'file selected {full_path}')

    def get_all_expanded(self, item=None, path=[]):
        # Initialize the item with the root item if it's None
        if item is None:
            item = self.tree_widget.invisibleRootItem()

        expanded_paths = []
        for i in range(item.childCount()):
            child = item.child(i)
            child_path = path + [child.text(0)]
            if child.isExpanded():
                expanded_paths.append('/'.join(child_path))
                expanded_paths += self.get_all_expanded(child, child_path)

        return expanded_paths

    def set_all_expanded(self, expanded_paths, item=None, path=[]):
        # Initialize the item with the root item if it's None
        if item is None:
            item = self.tree_widget.invisibleRootItem()

        for i in range(item.childCount()):
            child = item.child(i)
            child_path = path + [child.text(0)]
            full_path = '/'.join(child_path)
            if full_path in expanded_paths:
                self.tree_widget.expandItem(child)
                self.set_all_expanded(expanded_paths, child, child_path)

    def reload_data(self, new_data):
        self.data = new_data
        expanded = self.get_all_expanded()
        self.tree_widget.clear()
        self.add_dict_to_tree(self.data, self.tree_widget)
        self.set_all_expanded(expanded)

    def add_dict_to_tree(self, data, tree_item):
        for key, value in data.items():
            if isinstance(value, dict):
                parent = QTreeWidgetItem(tree_item)
                parent.setText(0, key)
                parent.setIcon(0, QIcon('folder_closed_icon2.png'))
                self.add_dict_to_tree(value, parent)
            else:
                leaf = QTreeWidgetItem(tree_item)
                leaf.setText(0, key)  # Only show the key
                leaf.setIcon(0, QIcon('document_icon.png'))

    def memory_initial_load(self, data):
        self.log('memory_initial_load', f'memory_initial_load({data})')
        self.reload_data(data['record'])

    def get_index(self, item):
        # Initialize an empty list to store the path
        path = []
        # Loop while there is a parent item
        while item:
            # Prepend the text of the item (i.e., the key) to the path
            path.insert(0, item.text(0))
            # Move up to the parent item
            item = item.parent()
        # Return the path
        return path

    def get_data(self, path):
        ele = self.data
        for idx in path:
            ele = ele[idx]
        return ele

    def on_context_menu(self, point):
        # Create QMenu
        context_menu = QMenu(self)

        # Create actions
        delete_action = QAction("Delete", self)
        new_dir_action = QAction("Create New Directory", self)
        new_prompt_action = QAction("Create New Prompt", self)

        # Add actions to menu
        context_menu.addAction(delete_action)
        context_menu.addAction(new_dir_action)
        context_menu.addAction(new_prompt_action)

        # Connect actions to custom slot methods
        delete_action.triggered.connect(self.delete_memory)
        new_dir_action.triggered.connect(self.create_directory)
        new_prompt_action.triggered.connect(self.create_new_prompt)

        # Show context menu
        context_menu.exec_(self.tree_widget.mapToGlobal(point))

    def delete_memory(self):
        current_item = self.tree_widget.currentItem()
        path = self.get_index(current_item)
        data = self.get_data(path)
        if type(data) is dict:
            file_type = 'Directory'
        else:
            file_type = 'File'

        full_path_name = '/'.join(path)
        self.log('delete_item', f"Delete of {file_type} {full_path_name}")
        record = {'full_path_name': full_path_name}
        msg = {'cmd': 'delete', 'object': 'memory', 'cb': 'cb_delete_memory', 'record': record}
        SEND(msg)

    def cb_delete_memory(self, msg):
        if msg['rc'] != 'Okay':
            self.log('cb_delete_memory', f"Error: delete_memory({msg['record']['full_path_name']}) reason {msg['reason']}")
            return
        self.log('cb_delete_memory', f"delete_memory({msg['record']['full_path_name']}) complete")

    def create_directory(self):
        current_item = self.tree_widget.currentItem()
        path = self.get_index(current_item)
        ele = self.get_data(path)
        if type(ele) is not dict:
            path.pop()      # Dump file name
        full_path = '/'.join(path)
        name, ok = QInputDialog.getText(self, "Directory Name", "Enter Name of new folder:")
        if ok:
            # The user clicked "OK" and provided a valid input
            full_path_name = f"{full_path}/{name}"
            record = {'prompt_name': full_path_name}
            SEND({'cmd': 'create', 'cb': 'cb_create_directory', 'object': 'directory', 'record': record})
            self.log("create_directory", f"call create_directory({full_path_name})")

    def cb_create_directory(self, msg):
        if msg['rc'] == 'Okay':
            self.log('cb_create_directory', f"cb_create_directory({msg['record']['prompt_name']}) successful")
        else:
            self.log('cb_create_directory', f"cb_create_directory({msg['record']['prompt_name']}) failed reason: {msg['reason']}")

    def create_new_prompt(self):
        current_item = self.tree_widget.currentItem()
        path = self.get_index(current_item)
        ele = self.get_data(path)
        if type(ele) is not dict:
            path.pop()      # Dump file name
        full_path = '/'.join(path)
        name, ok = QInputDialog.getText(self, "File Name", "Enter Name of new file:")
        if ok:
            # The user clicked "OK" and provided a valid input
            full_path_name = f"{full_path}/{name}"
            record = {'prompt_name': full_path_name, 'text': ''}
            SEND({'cmd': 'write', 'cb': 'cb_write_memory', 'object': 'memory', 'record': record})
            self.log("write_memory", f"call write_memory({full_path_name})")

    def cb_write_memory(self, msg):
        if msg['rc'] == 'Okay':
            self.log('cb_write_memory', f"cb_write_memory({msg['record']['prompt_name']}) successful")
        else:
            self.log('cb_write_memory', f"cb_write_memory({msg['record']['prompt_name']}) failed reason: {msg['reason']}")


    def memory_update(self, msg):
        self.log('memory_update', f'memory_update({msg})')
        record = msg['record']
        mask = record['mask']
        path = record['path']
        name = record['name']
        content = record['content']
        if 'delete' in mask:
            ele = self.get_data(path)
            del ele[name]
            self.log('memory_update', f"memory_update({mask}, {path}/{name}) deleted")
        elif 'create' in mask:
            ele = self.get_data(path)
            if 'is_dir' in mask:
                ele[name] = {}
            else:
                ele[name] = content
            self.log('memory_update', f"memory_update({mask}, {path}/{name}) created")
        elif 'modify' in mask:
            ele = self.get_data(path)
            ele[name] = content
            self.log('memory_update', f"memory_update({mask}, {path}/{name}) modified")
        # Update GUI
        self.reload_data(self.data)



if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    with open("prompt_data.json", "r") as file:
        data = json.load(file)
    app = QApplication([])
    widget = PromptTree(None)
    widget.memory_initial_load({'record': data})
    widget.show()
    app.exec()
