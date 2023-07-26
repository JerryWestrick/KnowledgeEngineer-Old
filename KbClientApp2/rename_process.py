import sys
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout


class RenameProcessDialog(QDialog):
    name_changed = pyqtSignal(str)

    def __init__(self, old_name, parent=None):
        super(RenameProcessDialog, self).__init__(parent)
        self.setWindowTitle("Rename Process")
        self.old_name = old_name
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.label_new_name = QLabel("Enter new process name:")
        self.line_edit = QLineEdit(self.old_name)
        self.button_rename = QPushButton("Rename")
        self.button_cancel = QPushButton("Cancel")

        self.button_rename.clicked.connect(self.rename_process)
        self.button_cancel.clicked.connect(self.close)

        layout.addWidget(self.label_new_name)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button_rename)
        layout.addWidget(self.button_cancel)

        self.setLayout(layout)

    def rename_process(self):
        new_name = self.line_edit.text()
        self.parent().selected_process = new_name  # Update the calling widget's selected_process
        self.close()


def main():
    app = QApplication(sys.argv)
    app.selected_process = "Process Old Name"  # Replace this with the actual name of the process
    RenameProcessDialog(app.selected_process,  app).exec_()
    print(app.selected_process)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
