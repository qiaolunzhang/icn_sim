# -*- coding: utf-8 -*-
import select
import socket
import struct
import os
from datetime import datetime

#_HOST = '127.0.0.1'
#_HOST = '192.168.80.135'
#_PORT = 10000


class Router:
    MAX_WAITING_CONNECTIONS = 100
    RECV_BUFFER = 4096
    RECV_msg_content = 4
    RECV_MSG_TYPE_LEN = 4

    def __init__(self):
        # 用于保存文件名
        self.file_number = 1
        # store the fib form
        self.fib_dic = {}
        # store the pit form
        self.pit_dic = {}
        # store the cs form
        self.cs_dic = {}

        self.host = ''
        self.port = 20000
        self.connections = [] # collects all the incoming connections
        self.out_conn_dic = {} # collects all the outcoming connections
        self.ip_to_sock_dic = {}
        self.load_config()
        self.log_init()
        try:
            self.firewall_init()
        except Exception, e:
            print(Exception, ", ", e)
        self._run()


    def firewall_init(self):
        try:
            self.firewall_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.firewall_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.firewall_socket.connect(("192.168.80.136", 5252))
            self.firewall_socket.send('5000')
            # 用掉firewall回复的确认
            firewall_result = self.firewall_socket.recv(4096)
            print("\n")
            print(firewall_result, '\n')
        except Exception, e:
            print(Exception, ", ", e)


    def log_init(self):
        try:
            self.log_file = open("./log/router.log", "w+")
            self.log_file.close()
        except Exception, e:
            print(Exception, ", ", e)


    def load_config(self):
        try:
            with open('./config/router.conf') as f:
                for line in f:
                    if line[0] != '#':
                        if line[0] == 'local_ip':
                            self.host = line[1]
                            self.port = line[2]
                        line = line.split()
                        self.fib_dic[line[0]] = line[1]

            #print(self.fib_dic)
        except Exception, e:
            print(Exception, ", ", e)
            print("Failed to load the config file")
            raise SystemExit

        try:
            if not os._exists('./cache/'):
                os.mkdir('./cache')
        except:
            return

    def _bind_socket(self):
        """
        Create the sever socket and bind it to the given host and port
        :return:
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Now binding socket, host is ", self.host, " port is ", self.port)
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
            except Exception, e:
                print(Exception, ", ", e)
                print("Failed to unpack the package type")
                return
        # 如果包里头没有内容，那就并不做处理
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
                # sock.send(data)
                print("The received data is ", data, 'the length is', len(data))
                self._process_packet(sock, packet_type, data_origin, data)
            except Exception, e:
                print(Exception, ", ", e)
                print("Failed to unpack the packet length")

    def _process_packet(self, sock, typ_content, data_origin, data):
        print("\n")
        print("Now process the packet type: ", typ_content)
        print("The pit table is: \n")
        print(self.pit_dic)
        print("\n")
        print("The cs table is: \n")
        print(self.cs_dic)

        print()
        if typ_content == 1:
            # log: type 1
            try:
                # consumer收到了兴趣包, 在log文件下方附加
                with open("./log/router.log", 'a+') as f:
                    time_now = str(datetime.now())
                    packet_log = time_now + " receive interest " + data + ' 1 ' + '\n'
                    f.write(packet_log)
            except Exception, e:
                print(Exception, ", ", e)


            # 如果cs表里头有那么就直接发
            #@todo 根据content name查询服务器
            self.firewall_socket.send(data)
            firewall_result = self.firewall_socket.recv(4096)
            print("The result is ", firewall_result)
            if firewall_result == '0':
                return
            if data in self.cs_dic.keys():
                # 如果cs表里头有，那么直接读取，然后返回
                try:
                    data_location = self.cs_dic[data]
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
                    return
                except Exception, e:
                    print(Exception, ", ", e)
                    return

            # 如果pit表里头请求过
            #@todo 需要解决多次请求问题，同一个客户端多次请求，以及不同客户端的再次请求,那么pit表里头放得就是一个列表了
            if data in self.pit_dic.keys():
                return
            # 如果都没有
            try:
                next_hop_ip = self.fib_dic[data]
                if next_hop_ip in self.out_conn_dic.keys():
                    self.out_conn_dic[next_hop_ip].send(data_origin)
                else:
                    sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock_client.connect((self.fib_dic[data], 10000))

                    self.out_conn_dic[next_hop_ip] = sock_client
                    self.ip_to_sock_dic[next_hop_ip] = sock_client
                    self.connections.append(sock_client)

                    sock_client.send(data_origin)
                    print("Send the packet to ", self.fib_dic[data])
                # 然后改变pit表
                self.pit_dic[data] = sock
            except Exception, e:
                print(Exception, ", ", e)

            print("\n****************************************************\n")
        elif typ_content == 2:
            print("Succeed to get back packet")
            content_name_len_pack = data[:4]
            try:
                content_name_len = struct.unpack('>I', content_name_len_pack)[0]
                print("Content name length is ", content_name_len)
                content_name = data[4: 4 + content_name_len]
                print("Content name is ", content_name)

                # log type 2:
                try:
                    # consumer收到了兴趣包, 在log文件下方附加
                    with open("./log/router.log", 'a+') as f:
                        time_now = str(datetime.now())
                        packet_log = time_now + " receive data " + data + ' 1 ' + '\n'
                        f.write(packet_log)
                except Exception, e:
                    print(Exception, ", ", e)

                content = data[4 + content_name_len : ]
                if content_name in self.pit_dic.keys():
                    # 缓存
                    file_name = './cache/file_' + str(self.file_number)
                    self.file_number = self.file_number + 1
                    f = open(file_name, 'wb')
                    f.write(content)
                    f.close()
                    # cs_dic内添加已经缓存的内容
                    self.cs_dic[content_name] = file_name
                    # 发送给请求方
                    self.pit_dic[content_name].send(data_origin)
                    # pit_dic删除已经获得的内容发送给请求方
                    del self.pit_dic[content_name]
                else:
                    return

                print("\n****************************************************\n")
            except Exception, e:
                print(Exception, ", ", e)
                print("\n****************************************************\n")

    def _run(self):
        #todo 对于新来的socket，开一个线程，进行计时，如果超时没有收到另一个方向发回来的包，就关闭这个线程, 其中也有对pit表的处理
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
                                self.ip_to_sock_dic[client_address[0]] = client_socket
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


r = Router()
