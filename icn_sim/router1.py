# -*- coding: utf-8 -*-
import select
import socket
import struct
import os
from datetime import datetime

import utils

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
        self.firewall_host = ''
        self.firewall_port = 11111
        self.visualize_host = ''
        self.visualize_port = ''
        self.connections = [] # collects all the incoming connections
        self.out_conn_dic = {} # collects all the outcoming connections
        self.ip_to_sock_dic = {}
        self.sock_to_ip_dic = {}
        self.load_config()

        self.log_init()
        self.visualize_init()
        #@todo 暂时不加入防火墙功能，用于log调试
        self.firewall_enable = True
        if self.firewall_enable:
            try:
                self.firewall_init()
            except Exception, e:
                print(Exception, ", ", e)
        self._run()

    def tables_log_init(self):
        try:
            self.fib_log_file = open("./tables/fib_router1.csv", "w+")
            #self.tables_log_file.write("src,dst,type,pass,time,content_name"+'\n')
            self.fib_log_file.close()
        except Exception, e:
            print(Exception, ", ", e)
        try:
            self.pit_log_file = open("./tables/pit_router1.csv", "w+")
            self.pit_log_file.close()
        except Exception, e:
            print(Exception, ", ", e)
        try:
            self.cs_log_file = open("./tables/cs_router1.csv", "w+")
            self.cs_log_file.close()
        except Exception, e:
            print(Exception, ", ", e)

    def firewall_init(self):
        try:
            self.firewall_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.firewall_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            #self.firewall_socket.connect((self.firewall_host, self.firewall_port))
            self.firewall_socket.connect((self.firewall_host, self.firewall_port))
            self.firewall_socket.send('5000')
            # 用掉firewall回复的确认
            firewall_result = self.firewall_socket.recv(4096)
            print(firewall_result)
        except Exception, e:
            print(Exception, ", ", e)

    def visualize_init(self):
        try:
            self.visualize_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.visualize_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.visualize_socket.bind((self.host, 0))
            self.visualize_socket.connect((self.visualize_host, self.visualize_port))
            print("Connect to visualize server, host is ", self.visualize_host, "port is ", self.visualize_port)
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
            with open('./config/router1.conf') as f:
                for line in f:
                    if line[0] != '#':
                        line = line.split()
                        if line[0] == 'local_ip':
                            self.host = line[1]
                            self.port = int(line[2])
                            continue
                        if line[0] == 'visual_ip':
                            self.visualize_host = line[1]
                            self.visualize_port = int(line[2])
                            continue
                        if line[0] == 'firewall_ip':
                            self.firewall_host = line[1]
                            self.firewall_port = int(line[2])
                            continue
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
        print("Now binding the socket, host is ", self.host, " port is ", self.port)
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

    def _process_packet_interest(self, sock, typ_content, data_origin, data):
        # log: type 1
        #@todo 根据是否拦截来发送最后面的0,1表示
        time_now = datetime.now()
        time_num_str = str(time_now.year) + str(time_now.month) + str(time_now.day) + str(time_now.hour) + str(time_now.minute) + str(time_now.second) + str(time_now.microsecond)
        try:
            # consumer收到了兴趣包, 在log文件下方附加
            with open("./log/router.log", 'a+') as f:
                # |src,    |dst,    |type,   |pass,  |time
                # |0,      |      1,|      1,|     1,|2018526221022933988
                packet_log = self.host + ", " + self.sock_to_ip_dic[sock] + ", " + "1, " + "1, " + time_num_str + ", " + data
                #packet_log = time_num_str + " interest " + self.sock_to_ip_dic[sock] + " " + self.host + " " + data + ' 1 '
                f.write(packet_log+'\n')
                #self.visualize_socket.send(packet_log)
                print("Send the data to visualize server")
        except Exception, e:
            print(Exception, ", ", e)

        # 如果cs表里头有那么就直接发
        #  根据content name查询服务器
        if self.firewall_enable:
            self.firewall_socket.send(data)
            firewall_result = self.firewall_socket.recv(4096)
            print("The result is ", firewall_result)
            if firewall_result == '0':
                packet_log = self.host + ", " + self.sock_to_ip_dic[sock] + ", " + "1, " + "0, " + time_num_str + ", " + data
                self.visualize_socket.send(packet_log)
                print("The message is blocked")
                return

        packet_log = self.host + ", " + self.sock_to_ip_dic[sock] + ", " + "1, " + "1, " + time_num_str + ", " + data
        self.visualize_socket.send(packet_log)
        print("ok to send to visualize")

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
        # @todo 需要解决多次请求问题，同一个客户端多次请求，以及不同客户端的再次请求,那么pit表里头放得就是一个列表了
        if data in self.pit_dic.keys():
            return
        # 如果都没有
        try:
            next_hop_ip = self.fib_dic[data]
            if next_hop_ip in self.out_conn_dic.keys():
                self.out_conn_dic[next_hop_ip].send(data_origin)
            else:
                sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print("Send the next hop: ", self.fib_dic[data], " ", 1000)
                sock_client.bind((self.host, 0))
                sock_client.connect((self.fib_dic[data], 10000))

                self.out_conn_dic[next_hop_ip] = sock_client
                self.ip_to_sock_dic[next_hop_ip] = sock_client
                self.sock_to_ip_dic[sock_client] = next_hop_ip
                self.connections.append(sock_client)

                print("Send the packet to ", self.fib_dic[data])
                sock_client.send(data_origin)
            # 然后改变pit表
            self.pit_dic[data] = sock
        except Exception, e:
            print(Exception, ", ", e)

        print("\n****************************************************\n")

    def _process_packet_data(self, sock, typ_content, data_origin, data):
        print("Succeed to get back packet")
        content_name_len_pack = data[:4]
        try:
            content_name_len = struct.unpack('>I', content_name_len_pack)[0]
            print("Content name length is ", content_name_len)
            content_name = data[4: 4 + content_name_len]
            print("Content name is ", content_name)

            #@todo 发送数据包log
            # log type 2:
            time_now = datetime.now()
            time_num_str = str(time_now.year) + str(time_now.month) + str(time_now.day) + str(time_now.hour) + str(time_now.minute) + str(time_now.second) + str(time_now.microsecond)
            try:
                # consumer收到了兴趣包, 在log文件下方附加
                with open("./log/router.log", 'a+') as f:
                    packet_log = time_num_str + " data " + self.sock_to_ip_dic[sock] + " " + self.host + " " + content_name + ' 1 '
                    # sock.send(packet_log)
                    f.write(packet_log + '\n')
                    #self.visualize_socket.send(packet_log)
            except Exception, e:
                print(Exception, ", ", e)

            packet_log = self.host + ", " + self.sock_to_ip_dic[sock] + ", " + "2, " + "1, " + time_num_str + ", " + content_name
            self.visualize_socket.send(packet_log)

            content = data[4 + content_name_len:]
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


    def _process_packet(self, sock, typ_content, data_origin, data):
        print("\n")
        print("Now process the packet type: ", typ_content)
        print("The fib table is: \n")
        print(self.fib_dic)
        print("The pit table is: \n")
        print(self.pit_dic)
        print("\n")
        print("The cs table is: \n")
        print(self.cs_dic)

        print()
        if typ_content == 1:
            self._process_packet_interest(sock, typ_content, data_origin, data);

        elif typ_content == 2:
            self._process_packet_data(sock, typ_content, data_origin, data)

        try:
            with open("./tables/fib_router1.csv", "w+") as f:
                for i in self.fib_dic.keys():
                    f.write(i + " , " + self.fib_dic[i]+'\n')
            with open("./tables/pit_router1.csv", "w+") as f:
                for i in self.pit_dic.keys():
                    f.write(i + " , " + self.pit_dic[i]+'\n')
            with open("./tables/cs_router1.csv", "w+") as f:
                for i in self.cs_dic.keys():
                    f.write(i + " , " + self.cs_dic[i]+'\n')
        except Exception, e:
            print(Exception, ", ", e)


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
                                self.sock_to_ip_dic[client_socket] = client_address[0]
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
