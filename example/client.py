import sys
import socket
import threading, time
import os
import wx
import telnetlib
from time import sleep
import _thread

# global variable
isNormar = True
s=''

class MainWindow(wx.Frame):
    """We simply derive a new class of Frame."""
    def __init__(self, parent,id, title, size):
        wx.Frame.__init__(self, parent, id, title)
        self.SetSize(size)
        self.Center()
        self.chatFrame = wx.TextCtrl(self, pos=(5, 5), size=(490, 310), style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.message = wx.TextCtrl(self, pos=(5, 320), size=(490, 150))
        self.contact = wx.TextCtrl(self,pos=(500,35),size=(200,280))

        #set buttons
        self.txtButton = wx.Button(self, label="TXTout", pos=(600, 380), size=(58, 25))
        self.sendButton = wx.Button(self, label="Send", pos=(520, 340), size=(58, 25))
        self.usersButton = wx.Button(self, label="Users", pos=(520, 380), size=(58, 25))
        self.closeButton = wx.Button(self, label="Close", pos=(520, 420), size=(58, 25))
        self.receiveButton=wx.Button(self,label="Receive",pos=(600,340),size=(58,25))
        self.sendButton.Bind(wx.EVT_BUTTON, self.send)
        self.usersButton.Bind(wx.EVT_BUTTON, self.lookUsers)
        self.closeButton.Bind(wx.EVT_BUTTON, self.close)
        self.receiveButton.Bind(wx.EVT_BUTTON,self.receive)
        self.txtButton.Bind(wx.EVT_BUTTON, self.txtout)
        #thread.start_new_thread(self.receive, ())

        #set background image
        try:
            image_file = 'rs-coldplay-0bc8e100-1674-49c6-a92c-4575ef89edd9.jpg'
            to_bmp_image = wx.Image(image_file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            self.bitmap = wx.StaticBitmap(self, -1, to_bmp_image, (0, 0))
            image_width = to_bmp_image.GetWidth()
            image_height = to_bmp_image.GetHeight()
            set_title = '%s %d x %d' % (image_file, to_bmp_image.GetWidth(), to_bmp_image.GetHeight())
        except IOError:
            print('Image file %s not found' % image_file)
            raise SystemExit

        #set special font
        self.contactlist = wx.StaticText(self,label="Contact list", size=(200,40), pos=(500,10))
        font = wx.Font(18, wx.ROMAN, wx.ITALIC, wx.NORMAL)
        self.contactlist.SetFont(font)

        self.other_usr = '0' #target
        self.username = 'a'
        self.chatFrame.AppendText('Please input your name:')
        self.n = 0  #used to send the username
        self.s = s
        self.data = 'abc'
        #self.m_panel1.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        #self.panel = wx.Panel(self)
        #self.panel.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBack)
        self.Show()

    def send(self,event):
        if self.n==0:
            msgg = str(self.message.GetLineText(0)).strip()
            self.username=msgg
            self.s.send('login|%s' %msgg)
            self.n = self.n+1
            self.message.Clear()
        else:
            msgg = str(self.message.GetLineText(0)).strip()
            #print '%s' % msgg
            data1 = msgg.split('_')

            if data1[0] == 'chat':
                self.other_usr = data1[1]

            if msgg == 'exit':
                self.s.send('exit')
                self.chatFrame.AppendText( '\n' +  self.username + ': ' + msgg)
                self.message.Clear()

            if (msgg != '') & (self.other_usr != '') & (msgg != 'exit') :
                #print '%s' % self.other_usr
                self.s.send("talk|%s|%s" % (self.other_usr, msgg))
                self.chatFrame.AppendText('\n'+ self.username + ': ' + msgg  )
                self.message.Clear()

    def lookUsers(self, event):
        self.s.send("user|")

    def close(self, event):
        self.chatFrame.AppendText('logout\n')
        #con.close()
        self.Close()

    def receive(self,event):
        self.data = self.s.recv(1024)
        msg = self.data.split('|')
       # print 'hhhhhh %s'% self.data
#           result = con.read_very_eager()
        #if msg[0] == 'login':
        if msg[0] == 'login':
            self.chatFrame.AppendText(u'%s user has already logged in, start to chat' % msg[1])
            self.other_usr = msg[1]
            #print '1%s'%self.other_usr
        if msg[0] == 'user':
            self.contact.Clear()
            self.contact.AppendText(msg[1])
        else:
            #msg = self.data.split('\n')
            self.chatFrame.AppendText('\n')
            self.chatFrame.AppendText(msg[-1])

    def txtout(self, event):  #char history out
        fname = 'C:\Users\jiatu\Desktop\TXTout_%s.txt' % self.username
        fobj = open(fname, 'w')
        i = 0
        while (str(self.chatFrame.GetLineText(i)).strip()) != '':
            msgg = str(self.chatFrame.GetLineText(i)).strip()
            fobj.write(msgg)
            fobj.write('\n')
            i=i+1
        fobj.close()

if __name__ == "__main__":
    app = wx.App(False)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("127.0.0.1", 9999))

    MainWindow(None, -1, title='Chat Client', size=(500, 350))

    #    MainWindow(None, -1, title="Login", size=(280, 200))
    app.MainLoop()
    #main()
