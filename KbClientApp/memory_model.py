from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt


class MemoryNode:
    def __init__(self, key, value, parent=None):
        self.key = key
        self.value = value
        self.parent = parent
        self.children = []

        if isinstance(value, dict):
            for k, v in value.items():
                self.children.append(MemoryNode(k, v, self))


class MemoryModel(QAbstractItemModel):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.root = MemoryNode(None, data)

    def update(self, data):
        self.beginResetModel()
        self.root = MemoryNode(None, data)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return len(parent.internalPointer().children)
        return len(self.root.children)

    def columnCount(self, parent=QModelIndex()):
        return 2

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == Qt.DisplayRole:
            if index.column() == 0:
                return node.key
            if index.column() == 1:
                return str(node.value)

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        parent_node = index.internalPointer().parent

        if parent_node == self.root:
            return QModelIndex()

        return self.createIndex(parent_node.parent.children.index(parent_node), 0, parent_node)

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parent_node = self.root
        else:
            parent_node = parent.internalPointer()

        return self.createIndex(row, column, parent_node.children[row])
