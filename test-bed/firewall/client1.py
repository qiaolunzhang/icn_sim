# -*- coding:utf-8 -*-
import socket, select, string, sys,os,psutil
import gensim
HOST = '192.168.80.137'
PORT = 5252
ID = '1'

blacklist = [u'邪教']

class ChatClient:
    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()
        self.load_config()
        self.load_model()
        self.module_path = "wiki.zh.text.model"
        #@todo 后面需要去掉下面这行
        # self.judge_content_name(u'法轮功')

    def load_config(self):
        try:
            with open('./config/client.conf') as f:
                for line in f:
                    self.module_path = line
            #print(self.fib_dic)
        except Exception, e:
            print(Exception, ", ", e)
            print("Failed to load the config file")
            raise SystemExit

    def load_model(self):
        self.blacklist = blacklist
        self.model = gensim.models.Word2Vec.load(self.module_path)
        self.model.init_sims(replace=True)

    def judge_content_name(self, content_name):
        try:
            print("***********************************")
            print("\n Now blacklist is: ")
            print(self.blacklist)

            print("before convert: ", content_name)
            # convert content_name
            content_name = content_name.decode('utf-8')
            print("after convert: ", content_name)

            if content_name in blacklist:
                print("防火墙包含: ")
                for i in self.blacklist:
                    print(i)
                print("Content name is in blacklist.")
                return False

            for blacklist_element in blacklist:
                # 通过content name来生成
                content_name_result = self.model.most_similar(content_name)
                content_name_result_list = []

                for e in content_name_result:
                    content_name_result_list.append(e[0])
                #print("\n Content name result is ")
                print("\n 通过Content name推理出的词汇为：")
                for i in content_name_result_list:
                    print(i)
                #print(content_name_result_list)

                for i in content_name_result_list:
                    if i in self.blacklist:
                        self.blacklist.append(content_name)
                        print("The content name is in the result of content name result.")
                        return False
                # 通过blacklist来生成
                element_result = self.model.most_similar(blacklist_element)
                element_result_list = []
                for e in element_result:
                    element_result_list.append(e[0])
                print("\n Blacklist element ", blacklist_element)
                #print("\n Blacklist element result is ", element_result_list)
                print("\n 通过黑名单推理出来的词汇是：")
                for i in element_result_list:
                    print(i)

                if content_name in element_result_list:
                    self.blacklist.append(content_name)
                    print("The content name is in the result of blacklist result.")
                    return False
            return True
        except Exception, e:
            print(Exception, ", ", e)
            return True

    def connect(self):
        try:
            self.client_socket.connect((HOST, PORT))
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
