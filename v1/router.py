# -*- coding: utf-8 -*-
import select
import socket
import struct

#_HOST = '127.0.0.1'
_HOST = '192.168.80.135'
_PORT = 10000


class Router:
    MAX_WAITING_CONNECTIONS = 100
    RECV_BUFFER = 4096
    RECV_msg_content = 4
    RECV_MSG_TYPE_LEN = 4

    def __init__(self, host, port):
        # store the fib form
        self.fib_dic = {}
        # store the pit form
        self.pit_dic = {}
        # store the cs form
        self.cs_dic = {}

        self.host = host
        self.port = port
        self.connections = [] # collects all the incoming connections
        self.out_connections = [] # collects all the outcoming connections
        self.load_config()
        self._run()

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
        except:
            print("Failed to load the config file")
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
                data_origin = msg_content + typ_content
                sock.send(data)
                print("The received data is ", data, 'the length is', len(data))
                #@todo 还要将ip地址的处理加上去
                #@todo 根据包的类型，到底是兴趣包，还是数据包
                self._process_packet(packet_type, data_origin, data)
                #@todo 如果是兴趣包，新开一个socket，同时要改变表项
                #@todo 如果是数据包，同样要做相应处理
            except:
                print("Failed to unpack the packet length")

    def _process_packet(self, typ_content, data_origin, data):
        print("\nNow process the packet type: ", typ_content)
        if typ_content == 1:
            sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                #@todo 发送方有问题的话，会多一个\n
                sock_client.connect((self.fib_dic[data], 10000))
                sock_client.send(data_origin)
                #@todo 如何处理和router之间的数据，如果有连接了，两次收到相同的包会如何
                self.out_connections.append(sock_client)
                #sock_client.close()
                print("Send the packet to ", self.fib_dic[data])
            except Exception, e:
                print(Exception, ", ", e)
        elif typ_content == 2:
            print("Succeed to get back packet")

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


r = Router(_HOST, _PORT)
