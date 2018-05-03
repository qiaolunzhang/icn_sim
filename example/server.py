

import sys
import threading, time
import socket
#import User
import os
from time import sleep
import thread
import wx

class User:
    def __init__(self,skt,username='none',target='none'):
        self.skt=skt
        self.username=username
        self.target=target
    def send_msg(self,msg):
        self.skt.send(msg)
    def logout(self):
        self.skt.close()

# global variable
userlist = []
s = ''
n = 0
def hand_user_con(usr):
    try:
        isNormar = True
        while isNormar:
            data = usr.skt.recv(1024)
            time.sleep(1)
            msg = data.split('|')

            print '%s'%msg[0]
            if msg[0] == 'login':
                #print 'user [%s] login' % msg[1]
                usr.username = msg[1]
                #print '%s'%usr.target
                notice_other_usr(usr)
            if msg[0] == 'talk':
                data1 = msg[2].split('_')

                #print '%s  %s'%(data1[0],data1[1])
                if data1[0] == 'chat':
                    usr.target=data1[1]  #choose the chat object
                else:
                    #print '%s  %s' % (usr.target, msg[2])
                    usr.target = msg[1]
                    for usr1 in userlist:
                        if (usr1.target == usr.username) & (usr.target == '0'):
                            usr.target = usr1.username   #return the message
                    #print ("talk|%s|%s" % (usr.target, msg[2]))
                    send_msg(usr.target, msg[2])# dtg
            if msg[0] == 'user':
                users =  ''
                for usr3 in userlist:
                    print usr3.username
                    if ( (usr3.username != 'none') & (usr3.username != '0') ):
                        users = '%s \n %s' % (users, usr3.username)
                send_msg(usr.username, 'user|%s' % users)
            if msg[0] == 'exit':
                print 'user [%s] exit' % msg[0]
                isNormar = False
                #usr.close()
                userlist.remove(usr)
    except:
        isNormar = False

#
def notice_other_usr(usr):
    if (len(userlist) > 1):
        for i in range(0,len(userlist)-1):
            userlist[-1].skt.send(userlist[i].username)    #show the usrs who already signed in
            userlist[-1].skt.send(' ')
        userlist[-1].skt.send("\n")
        userlist[-1].skt.send(("%s" % 'Which one do you want to choose'))
        userlist[-1].skt.send("\n")
        userlist[-1].skt.send(("%s"%"Please enter 'chat_the username you want to chat with'"))
    else:
        print 'The one user'


def send_msg(username, msg):
    for usr in userlist:
        if (usr.username == username):
            usr.skt.send(msg)


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 9999))
    s.listen(5)

    #print 'waiting for connection...'
    while True:
        sock, addr = s.accept()  #
        user = User(sock)
        userlist.append(user)
        t = threading.Thread(target=hand_user_con, args=(user,));
        t.start()
    s.close()


if (__name__ == "__main__"):
    main()