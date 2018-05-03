import socket
import select
import sys
from thread import *
import pickle

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()

IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.bind((IP_address, Port))

while True:
    """Accepts a connection request and stores two parameters, 
    conn which is a socket object for that user, and addr which
    contains the IP address of the client that just connected"""
    conn, addr = server.accept()
    message = conn.recv(2048)
    if message:
        t = pickle.load(message)
        print(t)


server.close()
