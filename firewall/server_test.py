# -*- coding: utf-8 -*-
import select
import socket

inBufSize = 4096
outBufSize = 4096
CONNECTION_LIST = []
cpu=['','','','']
class ChatServer:
    def __init__(self,port=5252):
        # todo 使用socketserver来写
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind(('', port))
        self.serverSocket.listen(5)
        print "server wait for connect...."
        self.socketsMap = {}  # socket session字典 id : socket
        self.idMap = {} #socket session 字典 socket:id
        CONNECTION_LIST.append(self.serverSocket)

    def login(self,id,sock):#新用户登录
        print "%s login"%id
        self.socketsMap[id] = sock
        self.idMap[sock] = id
        sock.send('hello %s,you login successed'%id)
        CONNECTION_LIST.append(sock)#要在这里把socket加进来才行

    def chat(self,sock):#点对点聊天，发送消息格式id||信息
        try:
            data = sock.recv(inBufSize)
            print "content name = %s" % ( data)
            self.socketsMap['1'].send(data)
            data1 = self.socketsMap['1'].recv(inBufSize)
            self.socketsMap['2'].send(data)
            data2 = self.socketsMap['2'].recv(inBufSize)

            if (float(data1)>float(data2)):
                data1, data2 = data2, data1
                runid='1'
            else:
                runid='1'

            print "cpu rate of cpu 1 = %s" % ( data1)
            print "cpu rate of cpu 2 = %s" % ( data2)
            print "running id %s" %(runid)
            self.socketsMap['1'].send(runid)
            self.socketsMap['2'].send(runid)
            firewall_result = self.socketsMap[runid].recv(inBufSize)
            print "firewall result: %s" % ( firewall_result)
            sock.send(firewall_result)
        except Exception,e:
            print 'Unable to connect because of %s'%e
            sock.send("remote is offline")

    def socet_handle(self):
        while 1:
            # Get the list sockets which are ready to be read through select
            read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])
            for sock in read_sockets:
                # New connection
                if sock == self.serverSocket:#用户通过主socket（即服务器开始创建的 socket，一直处于监听状态）来登录
                    # Handle the case in which there is a new connection recieved through server_socket
                    sockfd, addr = self.serverSocket.accept()
                    id = sockfd.recv(2048)
                    self.login(id,sockfd)
                else:
                    self.chat(sock)

    def main(self):
        self.socet_handle()

if __name__ == '__main__':
    chat_server_obj = ChatServer()
    chat_server_obj.main()
