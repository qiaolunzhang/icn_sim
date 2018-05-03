# Python program to implement client side of chat room.
import socket
import select
import sys
import pickle

class test:
    def __init__(self):
        self.a = 1
        self.b = 2

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if len(sys.argv) != 3:
    print("Correct usage: script, IP address, port number")
    exit()
IP_address = str(sys.argv[1])
Port = int(sys.argv[2])
server.connect((IP_address, Port))

t = test()
t_str = pickle.dumps(t)
print("t_str is ", t_str)
server.send(t_str)

server.close()
