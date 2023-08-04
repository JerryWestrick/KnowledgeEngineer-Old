from PySide6.QtWidgets import QWidget, QVBoxLayout, QSplitter
from process_tree import ProcessTree
from step_editor import StepEditor
from prompt_tree import PromptTree
from prompt_editor import PromptEditor
from step_log import StepLog
from step_item_viewer import StepItemViewer

aStep = step =         {   "name": "Step 2",
            "prompt_name": "Prompts/Flask/Requirements to Components.pe",
            "ai": {"model": "gpt-3.5-turbo","temperature": 0,"max_tokens": 3000,"mode": "chat"},
            "storage_path": "Dynamic/System Components",
            "messages":[],
            "response":{},
            "answer": "",
            "files":{},
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "sp_cost": 0.0,
            "sc_cost": 0.0,
            "s_total": 0.0,
            "elapsed_time": 0.0
        }


class WorkBenchTab(QWidget):
    def __init__(self):
        super().__init__()

        self.process_tree = ProcessTree(self)
        self.step_editor = StepEditor(self)
        self.prompt_tree = PromptTree(self)
        self.prompt_editor = PromptEditor(self)
        self.step_log = StepLog(self, aStep)
        self.step_item_viewer = StepItemViewer(self)
        layout = QVBoxLayout(self)

        # Row 1
        splitter1 = QSplitter()
        splitter1.addWidget(self.process_tree)
        splitter1.addWidget(self.step_editor)
        layout.addWidget(splitter1)

        # Row 2
        splitter2 = QSplitter()
        splitter2.addWidget(self.prompt_tree)
        splitter2.addWidget(self.prompt_editor)
        layout.addWidget(splitter2)

        # Row 3
        splitter3 = QSplitter()
        splitter3.addWidget(self.step_log)
        splitter3.addWidget(self.step_item_viewer)
        layout.addWidget(splitter3)

        self.setLayout(layout)
