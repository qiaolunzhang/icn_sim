# -*- coding:utf-8 -*-
import socket, select, sys,os,psutil
HOST = '127.0.0.1'
PORT = 5252
ID = '2'

class ChatClient:
    def __init__(self):
        self.host = ""
        self.port = 0
        self.firewall_host = ""
        self.firewall_port = 0
        self.load_config()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.settimeout(2)
        self.connect()

    def load_config(self):
        try:
            with open('./config/client.conf') as f:
                for line in f:
                    if line[0] != '#':
                        line = line.split()
                        if line[0] == 'local_ip':
                            self.host = line[1]
                            self.port = int(line[2])
                            continue
                        if line[0] == 'firewall_ip':
                            self.firewall_host = line[1]
                            self.firewall_port = int(line[2])
                            continue
                        if line[0] == 'path':
                            self.module_path = line[1]
        except Exception, e:
            print(Exception, ", ", e)
            print("Failed to load the config file")
            raise SystemExit

    def connect(self):
        try:
            self.client_socket.bind((self.host, 0))
            self.client_socket.connect((self.firewall_host, self.firewall_port))
            self.client_socket.send(ID)
            data = self.client_socket.recv(4096)
            sys.stdout.write(data)
            self.prompt()
        except Exception,e:
            print('Unable to connect because of %s'%e)
            sys.exit()
        else:
            print('Connected to remote host. Start sending messages')
            self.prompt()


    def prompt(self):
        sys.stdout.write('\n<You> ')
        sys.stdout.flush()

    def socket_handler(self):
        while 1:
            rlist = [sys.stdin, self.client_socket]  # 接收列表
            read_list, write_list, error_list = select.select(rlist, [], [], 2)

            #change
            for sock in read_list:
                if sock == self.client_socket:
                    data = sock.recv(4096)
                    sys.stdout.write(data)
                    cpurate=str(psutil.cpu_percent(1))
                    sys.stdout.write('\n<CPU> ')
                    sys.stdout.write(cpurate)
                    self.client_socket.send(cpurate)
                    data = sock.recv(4096)
                    print("\n running id %s" % (data))
                    if (data=='2'):
                        print("\n true")
                        blackname='1'
                        self.client_socket.send(blackname)
                    else:
                        print("\n false")
                        continue
                    self.prompt()
                    # user entered a message

                else:
                    msg = sys.stdin.readline()
                    remote_id = raw_input("Please input remote id:")
                    msg_send = "%s||%s"%(remote_id,msg)
                    self.client_socket.send(msg_send)
                    self.prompt()

if __name__ == '__main__':
    chat_client_obj = ChatClient()
    chat_client_obj.socket_handler()
