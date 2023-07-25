import jsonpickle
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton

import json


class OutputEditor(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.init_ui()
        self.parent = parent

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a QTextEdit
        self.textEditor = QTextEdit()
        layout.addWidget(self.textEditor)

        self.setWindowTitle('Output Editor')
        self.show()

    def show_attribute_value(self, attribute, value):
        if attribute == "e_stats":
            stats = eval(value)
            html = '''<table border="0"><tr><th style="text-align:left;">Stat</th><th style="text-align:left;">Value</th></tr>'''
            for key in stats.keys():
                html += f"<tr><td>{key}</td><td>{stats[key]}</td></tr>"
            html += "</table>"
            self.textEditor.setHtml(html)
        elif attribute == "answer":
            html = f"<pre>{value}</pre>"
            self.textEditor.setHtml(html)
        elif attribute == "messages":
            color = {"user": "green", "system": "blue"}
            msgs = eval(value)
            html = '''<table border="1px"><tr><th width='50' align='left'>Role</th><th align='left'>Content</th></tr>'''
            for row in msgs:
                html += f"<tr><td><font color='{color[row['role']]}'>{row['role']}</font></td><td><font color='{color[row['role']]}'><pre>{row['content']}</pre></font></td></tr>"
            html += "</table>"
            self.textEditor.setHtml(html)
        elif attribute == "files":
            files = eval(value)
            html = '''<table border="0"><tr><th style="text-align:left;">File</th><th style="text-align:left;">Content</th></tr>'''
            for file_name in files.keys():
                html += f"<tr><td>{file_name}</td><td><pre>{files[file_name]}</pre></td></tr>"
            html += "</table>"
            self.textEditor.setHtml(html)
        elif attribute == "response":
            answer = eval(value)
            answer_str = jsonpickle.encode(answer, indent=4)
            html = f"<pre>{answer_str}</pre>"
            self.textEditor.setHtml(html)
        else:
            self.textEditor.setPlainText(value)



def main():
    app = QApplication([])
    ex = OutputEditor(None)
    app.exec_()


if __name__ == '__main__':
    main()
