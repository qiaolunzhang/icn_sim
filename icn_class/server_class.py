# -*- coding: utf-8 -*-
import select
import socket

inBufSize = 4096
outBufSize = 4096
CONNECTION_LIST = []

class ChatServer:
    def __init__(self,port=5251):
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
        except Exception:
            sock.send("remote is offline")
            sock.close()
        else:
            remote_id = data.split('||')[0]
            message = data.split('||')[1]
            print "id = %s,message = %s"%(remote_id,message)
            local_id = self.idMap[sock]
            if remote_id == 'all':
                self.broadcast(local_id,message)
            else:
                self.p2psend(local_id,message,remote_id)

    def p2psend(self,local_id,message,remote_id):
        remote_socket = self.socketsMap[remote_id]
        message_send = "%s said : %s" % (local_id, message)
        try:
            remote_socket.sendall(message_send)
        except Exception,e:
            print e
            remote_socket.close()
            CONNECTION_LIST.remove(remote_socket)

    def broadcast(self,local_id,message):
        for sock in CONNECTION_LIST:
            if sock == self.serverSocket:
                continue
            else:
                try:
                    message_send = "%s said : %s" % (local_id, message)
                    sock.send(message_send)
                except Exception,e:
                    print e
                    sock.close()
                    CONNECTION_LIST.remove(sock)
                    continue

    def socet_handle(self):
        while 1:
            # Get the list sockets which are ready to be read through select
            read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])
            for sock in read_sockets:
                # New connection
                if sock == self.serverSocket:#用户通过主socket（即服务器开始创建的 socket，一直处于监听状态）来登录
                    # Handle the case in which there is a new connection recieved through server_socket
                    sockfd, addr = self.serverSocket.accept()
                    id = sockfd.recv(100)
                    self.login(id,sockfd)
                else:
                    self.chat(sock)

    def main(self):
        self.socet_handle()
        self.serverSocket.close()

if __name__ == '__main__':
    chat_server_obj = ChatServer()
    chat_server_obj.main()
