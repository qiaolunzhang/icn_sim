# Python program to implement client side of chat room.
import socket
import select
import struct
import sys

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP_address = '127.0.0.1'
Port = 10000
server.connect((IP_address, Port))

while True:

    # maintains a list of possible input streams
    sockets_list = [sys.stdin, server]

    """ There are two possible input situations. Either the
    user wants to give  manual input to send to other people,
    or the server is sending a message  to be printed on the
    screen. Select returns from sockets_list, the stream that
    is reader for input. So for example, if the server wants
    to send a message, then the if condition will hold true
    below.If the user wants to send a message, the else
    condition will evaluate as true"""
    read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

    for socks in read_sockets:
        if socks == server:
            message = socks.recv(2048)
            print("The received message is: ", message)
            content_name = '/aueb.gr/'
            message = struct.pack('>I', len(message)) + \
                      struct.pack('>I', 1) + message
            server.send(message)
        else:
            message = sys.stdin.readline()
            message = struct.pack('>I', len(message)) + \
                      struct.pack('>I', 1) + message
            server.send(message)
            sys.stdout.write("Send the message: ")
            sys.stdout.write(message)
            sys.stdout.flush()
server.close()
