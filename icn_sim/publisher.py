# -*- coding: utf-8 -*-
import select
import socket
import struct
from datetime import datetime

#_HOST = '127.0.0.1'
_HOST = '192.168.80.134'
_PORT = 10000

class Publisher:
    MAX_WAITING_CONNECTIONS = 100
    RECV_BUFFER = 4096
    RECV_msg_content = 4
    RECV_MSG_TYPE_LEN = 4

    def __init__(self, host, port):
        # store the data
        self.data_dic = {}

        self.host = host
        self.port = port
        self.connections = [] # collects all the incoming connections
        self.load_config()
        self.log_init()
        self._run()

    def log_init(self):
        try:
            self.log_file = open("./log/publisher.log", "w+")
            self.log_file.close()
        except Exception, e:
            print(Exception, ", ", e)

    def load_config(self):
        try:
            with open('./config/publisher.conf') as f:
                for line in f:
                    if line[0] != '#':
                        line = line.split()
                        self.data_dic[line[0]] = line[1]

        except Exception, e:
            print(Exception, ", ", e)
            raise SystemExit

    def _bind_socket(self):
        """
        Create the sever socket and bind it to the given host and port
        :return:
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.MAX_WAITING_CONNECTIONS)
        self.connections.append(self.server_socket)

    def _receive(self, sock):
        """
        first get length
        then get type
        process
        :return:
        """
        data = None
        # Retrieves the first 4 bytes form message
        tot_len = 0
        msg_content = 0
        typ_content = 0

        # 得到数据包的总长度
        while tot_len < self.RECV_msg_content:
            msg_content = sock.recv(self.RECV_msg_content)
            tot_len += len(msg_content)
        tot_len = 0
        print("The length of data is ", len(msg_content))
        # 得到数据包的类型
        while tot_len < self.RECV_MSG_TYPE_LEN:
            typ_content = sock.recv(self.RECV_MSG_TYPE_LEN)
            tot_len += len(typ_content)
        print("The type of the packet is ", typ_content)
        if typ_content:
            try:
                packet_type = struct.unpack('>I', typ_content)[0]
                print("The package type is ", packet_type)
            except:
                print("Failed to unpack the package type")
        if msg_content:
            data = ''
            try:
                # Unpacks the message and gets the message length
                msg_content_unpack = struct.unpack('>I', msg_content)[0]
                tot_data_len = 0
                while tot_data_len < msg_content_unpack:
                    # Retrieves the chunk i-th chunk of RECV_BUFFER size
                    chunk = sock.recv(self.RECV_BUFFER)
                    # If there isn't the expected chunk...
                    if not chunk:
                        data = None
                        break # ... Simply breaks the loop
                    else:
                        # Merges the chunks content
                        data += chunk
                        tot_data_len += len(chunk)
                # 原始的整个数据包
                data_origin = msg_content + typ_content + data
                print("接受到的数据包为")
                print(data.decode('utf-8'))

                # log
                if packet_type == 1:
                    try:
                        # consumer收到了兴趣包, 在log文件下方附加
                        with open("./log/publisher.log", 'a+') as f:
                            time_now = str(datetime.now())
                            packet_log = time_now + " receive interest " + data + ' 1 ' + '\n'
                            f.write(packet_log)
                    except Exception, e:
                        print(Exception, ", ", e)

                elif packet_type == 2:
                    pass

                # 如果包的类型和content name都对上的话，就把数据包发给router
                try:
                    data_location = self.data_dic[data]
                    f = open(data_location, 'rb')
                    message = ''
                    l = f.read(1024)
                    while (l):
                        message = message + l
                        l = f.read(1024)
                    f.close()

                    content_name = data
                    content_len = struct.pack('>I', len(content_name))
                    message = content_len + content_name + message

                    message = struct.pack('>I', len(message)) + \
                              struct.pack('>I', 2) + message
                    sock.send(message)
                except Exception, e:
                    print(Exception, ", ", e)
            except Exception, e:
                print("Failed to unpack the packet length")
                print(Exception, ", ", e)
        print("\n**********************************************\n")

    def _run(self):
        self._bind_socket()
        while True:
            """
            Actually runs the server.
            """
            # Gets the list of sockets which are ready to be read through select non-blocking calls
            # The select has a timeout of 60 seconds
            try:
                ready_to_read, ready_to_write, in_error = select.select(self.connections, [], [], 60)
            except socket.error:
                continue
            else:
                for sock in ready_to_read:
                    if sock == self.server_socket:
                        if sock == self.server_socket:
                            try:
                                # Handles a new client connection
                                client_socket, client_address = self.server_socket.accept()
                            except socket.error:
                                break
                            else:
                                self.connections.append(client_socket)
                                print "Client (%s, %s) connected" % client_address
                        # ... else is an incoming client socket connection
                    else:
                        try:
                            #next_route_ip, data = self._receive(sock)
                            self._receive(sock)
                        except socket.error:
                            #print("Client is offline" % client_address)
                            sock.close()
                            self.connections.remove(sock)
                            continue


p = Publisher(_HOST, _PORT)