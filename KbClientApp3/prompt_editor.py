import json

import markdown as markdown
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy, \
    QTextEdit, QMainWindow, QDialog

from websocket import REGISTER_CALLBACK, SEND
from log_tab import LOG


class CustomTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super(CustomTextEdit, self).__init__(parent)
        self.setAcceptDrops(True)

    def log(self, action, message):
        LOG({'system': 'CustomTextEdit', 'action': action, 'message': message})

    def dragEnterEvent(self, event: QDragEnterEvent):
        # self.log('dragEnterEvent', f"CustomTextEdit:dragEnterEvent({event})")
        # if event.mimeData().hasText():
        event.accept()

    def dragMoveEvent(self, event: QDropEvent):
        # self.log('dragMoveEvent', f"...")
        event.accept()

    def dropEvent(self, event: QDropEvent):
        # self.log('dropEvent', f"dropEvent({event})")
        from_text = event.mimeData().text()
        # self.log("dropEvent", f"text:{from_text}")
        self.insertPlainText(f".include {from_text}\n")
        event.accept()


class PromptEditor(QWidget):
    def __init__(self, workbench):
        self.prompt_name = None
        self.prompt = None
        self.workbench = workbench
        super().__init__()

        self.setAcceptDrops(True)
        # VBox layout
        layout = QVBoxLayout(self)

        # First row
        h_box1 = QHBoxLayout()
        self.file_label = QLabel("Filename: None")
        h_box1.addWidget(self.file_label)
        h_box1.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.set_step_button = QPushButton("Set Step prompt_name: None")
        self.set_step_button.clicked.connect(self.set_step_prompt_name)
        h_box1.addWidget(self.set_step_button)
        layout.addLayout(h_box1)

        # Second row
        self.text_edit = CustomTextEdit()
        self.text_edit.textChanged.connect(lambda: self.save_button.setEnabled(True))
        # self.text_edit.setAcceptDrops(True)
        layout.addWidget(self.text_edit)

        # Third row
        h_box3 = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.write_memory)
        h_box3.addWidget(self.save_button)
        h_box3.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.md_button = QPushButton("Markdown")
        self.md_button.clicked.connect(self.md_memory)
        h_box3.addWidget(self.md_button)
        self.test_button = QPushButton("Test")
        self.test_button.clicked.connect(self.test_memory)
        h_box3.addWidget(self.test_button)
        layout.addLayout(h_box3)

        self.setLayout(layout)
        REGISTER_CALLBACK(self, method_list=['memory_update'])

    def log(self, action, message):
        LOG({'system': 'PromptEditor', 'action': action, 'message': message})

    # def dropEvent(self, event):
    #     text = event.mimeData().text()
    #     self.text_edit.insertPlainText(f".include {text}")
    #     event.acceptProposedAction()

    def set_prompt(self, prompt_name, contents):
        self.prompt_name = prompt_name
        self.prompt = contents
        self.text_edit.setText(self.prompt)
        self.file_label.setText(f'File: {self.prompt_name}')
        self.set_step_button.setText(f'Set Step prompt: {self.prompt_name}')
        self.save_button.setEnabled(False)

    def memory_update(self, msg):
        self.log('memory_update', f'memory_update({msg})')
        prompt = '/'.join(msg['record']['path']) + '/' + msg['record']['name']
        if self.prompt_name == prompt:
            self.set_prompt(prompt, msg['record']['content'])
            self.save_button.setEnabled(False)

    def set_step_prompt_name(self):
        self.log('set_step_prompt_name', f'set_step_prompt_name({self.prompt_name})')
        self.workbench.step_editor.set_prompt_name(self.prompt_name)

    def test_memory(self):
        record = {'prompt_name': self.prompt_name}
        msg = {'cmd': 'test', 'object': 'memory', 'cb': 'cb_test_memory', 'record': record}
        SEND(msg)

    def md_memory(self):
        md_text = self.text_edit.toPlainText()
        html_content = markdown.markdown(md_text)
        self.text_edit.setHtml(html_content)

    def cb_test_memory(self, msg):
        if msg['rc'] == 'Fail':
            self.log("cb_test_memory", f"Error: cb_test_memory {self.prompt_name} failed reason: {msg['reason']}")
        else:
            self.log("cb_test_memory", f"cb_test_memory {self.prompt_name} confirmed")
            txt = f"{msg['record']['text']}"
            self.workbench.step_item_viewer.view_item('messages', txt)

    def write_memory(self):
        self.save_button.setEnabled(False)
        record = {'prompt_name': self.prompt_name, 'text': self.text_edit.toPlainText()}
        msg = {'cmd': 'write', 'object': 'memory', 'cb': 'cb_write_memory', 'record': record}
        SEND(msg)

    def cb_write_memory(self, msg):
        if msg['rc'] == 'Fail':
            self.log("cb_write_memory", f"Error: cb_write_memory {self.prompt_name} failed reason: {msg['reason']}")
        else:
            self.log("cb_write_memory", f"cb_write_memory {self.prompt_name} confirmed")
