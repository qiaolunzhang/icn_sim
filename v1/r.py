import select
import socket

_HOST = '127.0.0.1'
_PORT = 10000


class Router:
    MAX_WAITING_CONNECTIONS = 100
    RECV_BUFFER = 4096
    RECV_MSG_LEN = 4

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
        self.load_config()
        self._run()

    def load_config(self):
        try:
            with open('./config/router.conf') as f:
                for line in f:
                    if line[0] != '#':
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
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.MAX_WAITING_CONNECTIONS)
        self.connections.append(self.server_socket)

    def _run(self):
        #todo 对于新来的socket，开一个线程，进行计时，如果超时没有收到另一个方向发回来的包，就关闭这个线程
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
                                message = client_socket.recv(2048)
                                print(message)


        #@todo 下面这个可以先放着
        # 来一个新的包，首先发送，然后开一个线程，如果时间到了还没有结束
        # 首先删除pit中的记录，然后再关闭



r = Router(_HOST, _PORT)
