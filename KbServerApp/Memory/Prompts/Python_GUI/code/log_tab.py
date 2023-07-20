import json
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QMessageBox
from PyQt5.QtGui import QColor
import socket
from threading import Thread

class LogTab(QWidget):
    def __init__(self):
        super(LogTab, self).__init__()

        self.initUI()
        self.start_socket_client()

    def initUI(self):
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.display_object)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def display_object(self, item):
        obj = json.loads(item.text())
        obj_str = json.dumps(obj, indent=4)
        QMessageBox.information(self, "Log Entry", obj_str)

    def start_socket_client(self):
        # Define your server's host and port
        server_host = '127.0.0.1'
        server_port = 12345

        # Create a TCP/IP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Connect to the server
            client_socket.connect((server_host, server_port))

            # Start a separate thread to receive messages from the server
            receive_thread = Thread(target=self.receive_messages, args=(client_socket,))
            receive_thread.start()
        except ConnectionRefusedError:
            print('Server is not available.')
            client_socket.close()

    def receive_messages(self, client_socket):
        while True:
            try:
                # Receive the message from the server
                message = client_socket.recv(1024).decode()

                # Add the message to the log list
                self.add_log_entry(message)
            except ConnectionResetError:
                print('Server connection closed.')
                break

        # Close the client socket when the loop exits
        client_socket.close()

    def add_log_entry(self, entry):
        obj = json.loads(entry)
        item = QListWidgetItem(entry)
        item.setForeground(QColor('red') if len(self.list_widget) % 2 else QColor('blue'))
        self.list_widget.addItem(item)
