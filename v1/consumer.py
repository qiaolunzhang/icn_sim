# Python program to implement client side of chat room.
import socket
import select
import struct
import sys

IP_address = '127.0.0.1'
Port = 10000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    with open('./config/consumer.conf') as f:
        for line in f:
            if line[0] != '#':
                line = line.split()
                IP_address = line[0]
                Port = int(line[1])
except:
    print("failed to load config")


server.connect((IP_address, Port))

while True:
    # maintains a list of possible input streams
    sockets_list = [sys.stdin, server]

    read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048)
            print("The received message is: ", message)
        else:
            message = sys.stdin.readline()
            message = message[:-1]
            message = struct.pack('>I', len(message)) + \
                      struct.pack('>I', 1) + message
            server.send(message)
            sys.stdout.write("Send the message: ")
            sys.stdout.write(message)
            sys.stdout.write('\n')
            sys.stdout.flush()
server.close()
