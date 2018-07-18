# -*- coding: utf-8 -*-
# Python program to implement client side of chat room.
import socket
import select
import struct
import sys
from datetime import datetime

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
        self.router_host = ""
        self.router_port = 0
        self.visualize_host = ""
        self.visualize_port = 0
        self.sock_to_ip_dic = {}
        self.connections = [] # collects all the incoming connections
        self.load_config()
        self.log_init()
        self.visualize_init()
        self._run()


    def visualize_init(self):
        try:
            self.visualize_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.visualize_socket.bind((self.host, 0))
            self.visualize_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.visualize_socket.connect((self.visualize_host, self.visualize_port))
            print("Connect to visualize server, host is ", self.visualize_host, "port is ", self.visualize_port)
        except Exception, e:
            print(Exception, ", ", e)


    def log_init(self):
        try:
            # os.path.exists("./log/consumer.log"):
            self.log_file = open("./log/consumer.log", "w+")
            self.log_file.close()
        except Exception, e:
            print(Exception, ", ", e)


    def load_config(self):
        try:
            with open('./config/consumer.conf') as f:
                for line in f:
                    if line[0] != '#':
                        line = line.split()
                        if line[0] == 'local_ip':
                            self.host = line[1]
                            self.port = int(line[2])
                        if line[0] == 'router_ip':
                            self.router_host = line[1]
                            self.router_port = int(line[2])
                        if line[0] == 'visual_ip':
                            self.visualize_host= line[1]
                            self.visualize_port= int(line[2])

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
        self.server_socket.bind((self.host, 0))
        self.server_socket.connect((self.router_host, self.router_port))
        self.sock_to_ip_dic[self.server_socket] = self.router_host
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

        # if packet_type != 2:
        #    return

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
                # 对数据包和兴趣包采取不同的方式
                if packet_type == 1:
                    self._process_interest_packet(data)
                elif packet_type == 2:
                    self._process_data_packet(data, sock)
            except Exception, e:
                print("Failed to unpack the packet length")
                print(Exception, ", ", e)
        print("\n**********************************************\n")


    def _process_interest_packet(self, data):
        try:
            # consumer收到了兴趣包, 在log文件下方附加
            with open("./log/consumer.log", 'a+') as f:
                time_now = str(datetime.now())
                packet_log = time_now + " receive interest " + data + ' 0 ' + '\n'
                f.write(packet_log)
        except Exception, e:
            print(Exception, ", ", e)


    def _process_data_packet(self, data, sock):
        print("\n")
        print("Succeed to get back data packet")
        content_name_len_pack = data[:4]
        try:
            content_name_len = struct.unpack('>I', content_name_len_pack)[0]
            print("Content name length is ", content_name_len)
            content_name = data[4: 4 + content_name_len]
            print("Content name is ", content_name)
            content = data[4 + content_name_len : ]
            print("Get the data: ")
            # 解码成utf-8才能正常显示
            print(content.decode('utf-8'))
            # 记录成功接受
            with open('./log/consumer.log', 'a+') as f:
                time_now = str(datetime.now())
                packet_log = time_now + " receive data " + content_name + " 1 " + "\n"
                f.write(packet_log)
            time_now = datetime.now()
            time_num_str = str(time_now.year) + str(time_now.month) + str(time_now.day) + str(time_now.hour) + str(time_now.minute) + str(time_now.second) + str(time_now.microsecond)
            packet_log = self.host + ", " + self.sock_to_ip_dic[sock] + ", " + "2, " + "1, " + time_num_str + ", " + content_name
            self.visualize_socket.send(packet_log)
            print("ok to send to visualize")
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
                        # 保存真实发送的数据
                        message_log = message
                        message = struct.pack('>I', len(message)) + \
                                  struct.pack('>I', 1) + message
                        self.server_socket.send(message)

                        # 记录发送包
                        with open('./log/consumer.log', 'a+') as f:
                            time_now = str(datetime.now())
                            packet_log = time_now + " send interest " + message_log + " 1 " + "\n"
                            f.write(packet_log)

                        sys.stdout.write("Send the message: ")
                        sys.stdout.write(message_log)
                        sys.stdout.write('\n')
                        sys.stdout.flush()

p = Consumer(_HOST, _PORT)
