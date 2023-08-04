from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QFont, QTextOption
from PySide6.QtNetwork import QAbstractSocket
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QHBoxLayout, QGroupBox

from log_tab import LOG
from websocket import WebSocketClient

class ComsTab(QWidget):
    def __init__(self, url):
        super().__init__()

        # Initialize WebSocket client with initial URL
        self.webclient = WebSocketClient(url, self)

        # Create layout
        layout = QHBoxLayout()

        # Create widgets
        self.url_input = QLineEdit(url)
        self.connect_button = QPushButton('Connect')
        self.log_view = QTextEdit()
        # Set the fixed-width font and disable line wrapping for self.log_view
        fixed_font = QFont("Courier")
        self.log_view.setFont(fixed_font)
        self.log_view.setWordWrapMode(QTextOption.NoWrap)

        # Create stoplight labels
        self.red_light = QLabel("\N{BLACK LARGE CIRCLE}")
        self.yellow_light = QLabel("\N{BLACK LARGE CIRCLE}")
        self.green_light = QLabel("\N{BLACK LARGE CIRCLE}")
        self.red_light.setStyleSheet("color: darkred; font-size: 30px")
        self.yellow_light.setStyleSheet("color: olive; font-size: 30px")
        self.green_light.setStyleSheet("color: darkgreen; font-size: 30px")

        # Create QVBoxLayouts for the stoplight lights and the other widgets
        lights_layout = QVBoxLayout()
        widgets_layout = QVBoxLayout()

        # Add the stoplight lights to the lights_layout
        lights_layout.addWidget(self.red_light)
        lights_layout.addWidget(self.yellow_light)
        lights_layout.addWidget(self.green_light)

        # Create a QGroupBox for the stoplight lights
        lights_group = QGroupBox()
        lights_group.setLayout(lights_layout)

        connection_layout = QHBoxLayout()

        widgets_layout.addLayout(connection_layout)
        # Add the other widgets to the widgets_layout
        connection_layout.addWidget(self.connect_button)
        connection_layout.addWidget(QLabel("url"))
        connection_layout.addWidget(self.url_input)
        widgets_layout.addWidget(QLabel("Logs"))
        widgets_layout.addWidget(self.log_view)

        # Add the QGroupBox and the QVBoxLayout to the QHBoxLayout
        layout.addWidget(lights_group)
        layout.addLayout(widgets_layout)
        layout.setAlignment(lights_group, Qt.AlignTop)
        self.setLayout(layout)

        # Connect signals and slots
        self.connect_button.clicked.connect(self.toggle_connection)

    def toggle_connection(self):
        if self.webclient.state() != QAbstractSocket.SocketState.ConnectedState:
            self.webclient.connect_to_server()
        else:
            self.webclient.close_connection()
        # self.connect_button.setEnabled(False)

    def append_log(self, msg):
        timestamp = QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss.zzz')
        msg_str = f"{msg['message']}"
        self.log_view.append(f"[{timestamp}] {msg['action']:25} - {msg_str}")

    def update_lights(self, state):
        # Turn all lights Off...
        self.red_light.setStyleSheet("color: darkred; font-size: 30px")
        self.yellow_light.setStyleSheet("color: olive; font-size: 30px")
        self.green_light.setStyleSheet("color: darkgreen; font-size: 30px")

        # Turn on One Light
        match state:
            case QAbstractSocket.SocketState.ClosingState | \
                 QAbstractSocket.SocketState.ConnectingState:
                self.yellow_light.setStyleSheet("color: gold; font-size: 30px")
                self.connect_button.setText('Progress')
                self.connect_button.setEnabled(False)

            case QAbstractSocket.SocketState.ConnectedState:
                self.green_light.setStyleSheet("color: limegreen; font-size: 30px")
                self.connect_button.setText('Disconnect')
                self.connect_button.setEnabled(True)

            case QAbstractSocket.SocketState.UnconnectedState:
                self.red_light.setStyleSheet("color: red; font-size: 30px")
                self.connect_button.setText('Connect')
                self.connect_button.setEnabled(True)
