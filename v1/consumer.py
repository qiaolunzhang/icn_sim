# -*- coding: utf-8 -*-
# Python program to implement client side of chat room.
import socket
import select
import struct
import sys
import os

#_HOST = '192.168.80.134'
_HOST = '127.0.0.1'
_PORT = 10000


class Consumer:
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
            # os.path.exists("./log/consumer.log"):
            #@todo 打开配置文件,设置为类的一个东西
            self.log_file = open("./log/consumer.log", "w")
            self.log_file.close()
        except Exception, e:
            print(Exception, ", ", e)


    def load_config(self):
        try:
            with open('./config/consumer.conf') as f:
                for line in f:
                    if line[0] != '#':
                        line = line.split()
                        self.host = line[0]
                        self.port = int(line[1])
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
        self.server_socket.connect((self.host, self.port))
        self.connections.append(self.server_socket)
        self.connections.append(sys.stdin)

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
            except Exception, e:
                print(Exception, ", ", e)
                print("Failed to unpack the package type")

        if packet_type != 2:
            #@todo 记录接受失败
            return

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
                print("The received data is ", data, 'the length is', len(data))
                self._process_packet(data)
            except Exception, e:
                print("Failed to unpack the packet length")
                print(Exception, ", ", e)
        print("\n**********************************************\n")


    def _process_packet(self, data):
        print("\n")
        print("Succeed to get back data packet")
        content_name_len_pack = data[:4]
        try:
            content_name_len = struct.unpack('>I', content_name_len_pack)[0]
            print("Content name length is ", content_name_len)
            content_name = data[4: 4 + content_name_len]
            print("Content name is ", content_name)
            content = data[4 + content_name_len : ]
            print("Get the data: ", content)
            #@todo 记录成功接受
        except Exception, e:
            print(Exception, ", ", e)


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
                        try:
                            self._receive(sock)
                        except Exception, e:
                            print(Exception, ", ", e)
                        # ... else is an incoming server socket connection
                    else:
                        # 如果是用户输入
                        message = sys.stdin.readline()
                        message = message[:-1]
                        message = struct.pack('>I', len(message)) + \
                                  struct.pack('>I', 1) + message
                        self.server_socket.send(message)
                        #@todo 记录发送包
                        sys.stdout.write("Send the message: ")
                        sys.stdout.write(message)
                        sys.stdout.write('\n')
                        sys.stdout.flush()

p = Consumer(_HOST, _PORT)