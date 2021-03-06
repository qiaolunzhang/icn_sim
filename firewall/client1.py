# -*- coding:utf-8 -*-
import socket, select, string, sys,os,psutil
import gensim
HOST = '127.0.0.1'
PORT = 5252
ID = '1'

blacklist = [u'邪教']

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
        #self.module_path = "wiki.zh.text.model"
        self.load_model()
        #@todo 后面需要去掉下面这行
        # self.judge_content_name(u'法轮功')

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

    def load_model(self):
        self.blacklist = blacklist
        self.model = gensim.models.Word2Vec.load(self.module_path)
        #self.model = gensim.models.Word2Vec.load("/home/zhang/mycode/firewall-simple/wiki.zh.text.model")
        self.model.init_sims(replace=True)

    def judge_content_name(self, content_name):
        try:
            print("***********************************")
            print("\n 雾计算防火墙的威胁内容为: ")
            for i in self.blacklist:
                print(i)

            # print("before convert: ", content_name)
            content_name = content_name.decode('utf-8')
            # print("after convert: ", content_name)

            if content_name in blacklist:
                print("请求的内容在雾计算防火墙的威胁内容中: ")
                for i in self.blacklist:
                    print(i)
                return False

            possible_attack = []

            for blacklist_element in blacklist:
                # 通过content name来生成
                content_name_result = self.model.most_similar(content_name)
                content_name_result_list = []

                for e in content_name_result:
                    content_name_result_list.append(e[0])
                #print("\n Content name result is ")
                print("\n 根据语义和"),
                print(content_name),
                print("关联的威胁内容为: ")
                for i in content_name_result_list:
                    print(i)

                print("\n")
                for i in content_name_result_list:
                    if i in self.blacklist:
                        possible_attack.append(i)

                print("包含在雾计算防火墙中的威胁内容为: ")
                for i in possible_attack:
                    print(i)
                print("\n")

                for i in possible_attack:
                    attack = i
                    possible_element = self.model.most_similar(i)
                    possible_element_list = []
                    for i in possible_element:
                        possible_element_list.append(i[0])

                    if content_name in possible_element_list:
                        self.blacklist.append(content_name)
                        print("\n")
                        print(content_name),
                        print("是威胁内容")
                        print("和威胁内容——"),
                        print(attack),
                        print("对应")
                        print("\n")
                        print("雾计算防火墙规则已更新，现在的威胁内容为：")
                        for i in self.blacklist:
                            print(i)
                        return False

            return True
        except Exception, e:
            print(Exception, ", ", e)
            return True

    def connect(self):
        try:
            self.client_socket.bind((self.host, 0))
            print(self.firewall_host + " " + str(self.firewall_port))
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
                    content_name = sock.recv(4096)
                    sys.stdout.write(content_name)
                    cpurate=str(psutil.cpu_percent(1))
                    sys.stdout.write('\n<CPU> ')
                    sys.stdout.write(cpurate)
                    self.client_socket.send(cpurate)
                    # 如果是1的话就运行
                    check_run = sock.recv(4096)
                    print("\n running id %s" % (check_run))
                    if (check_run=='1'):
                        print("\n Now I'm going to run: ")
                        check_result = self.judge_content_name(content_name)
                        if check_result:
                            result_string = '1'
                        else:
                            result_string = '0'
                        self.client_socket.send(result_string)
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
