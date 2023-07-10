

from hardware.nidaq import Scanner

import socket
import sys

print("Python 3 running ...")

HOST = '127.0.0.1'
PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("Connected")

while True:
    text = input("Input to send to server:  ")
    print("Sending data...")
    s.sendall(text.encode())
    data = s.recv(1024).decode()
    print('Received from server: ' + data)
    
    # Kill check
    if data == 'EXIT':
        s.close()
        sys.exit()