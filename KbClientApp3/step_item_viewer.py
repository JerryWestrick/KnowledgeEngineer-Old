import json

import jsonpickle
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit


class StepItemViewer(QWidget):
    def __init__(self, workbench):
        self.workbench = workbench
        super().__init__()

        layout = QVBoxLayout(self)
        self.label = QLabel("Step Item Viewer")
        self.text_edit = QTextEdit()
        layout.addWidget(self.label)
        layout.addWidget(self.text_edit)

        self.setLayout(layout)

    def view_item(self, key, value):

        self.label.setText(key)
        match key:
            case 'name' | 'prompt_name' | 'storage_path':
                self.text_edit.setText(value)
            case 'ai':
                obj = eval(value)
                self.text_edit.setText(json.dumps(obj, indent=4))
            case 'e_stats':
                stats = eval(value)
                html = '''<table border="0"><tr><th style="text-align:left;">Stat</th><th style="text-align:left;">Value</th></tr>'''
                for key in stats.keys():
                    value = stats[key]
                    if key in ['sp_cost', 'sc_cost', 's_total', 'elapsed_time']:
                        value = round(value, 4)
                    html += f"<tr><td>{key}</td><td>{value}</td></tr>"
                html += "</table>"
                self.text_edit.setHtml(html)
            case 'answer':
                html = f"<pre>{value}</pre>"
                self.text_edit.setHtml(html)
            case "messages":
                color = {"user": "green", "system": "teal", "exec": "royalblue", "assistant": "goldenrod"}
                msgs = eval(value)
                html = '''<table border="1px"><tr><th width='50' align='left'>Role</th><th align='left'>Content</th></tr>'''
                for row in msgs:
                    html += f"<tr><td><font color='{color[row['role']]}'>{row['role']}</font></td><td><font color='{color[row['role']]}'><pre>{row['content']}</pre></font></td></tr>"
                html += "</table>"
                self.text_edit.setHtml(html)
            case "files":
                files = eval(value)
                html = '''<table border="0"><tr><th width='150' style="text-align:left;">File</th><th style="text-align:left;">Content</th></tr>'''
                for file_name in files.keys():
                    html += f"<tr><td>{file_name}</td><td><pre>{files[file_name]}</pre></td></tr>"
                html += "</table>"
                self.text_edit.setHtml(html)
            case "response":
                answer = eval(value)
                answer_str = jsonpickle.encode(answer, indent=4)
                html = f"<pre>{answer_str}</pre>"
                self.text_edit.setHtml(html)

