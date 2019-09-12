import socket
import time

# We'll limit ourself to a 40KB/sec maximum send rate
maxSendRateBytesPerSecond = (40*1024)

def ConvertSecondsToBytes(numSeconds):
   return numSeconds*maxSendRateBytesPerSecond

def ConvertBytesToSeconds(numBytes):
   return float(numBytes)/maxSendRateBytesPerSecond

#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.sendall('Hello, world')

# We'll add to this tally as we send() bytes, and subtract from
# at the schedule specified by (maxSendRateBytesPerSecond)
bytesAheadOfSchedule = 0

# Dummy data buffer, just for testing
dataBuf = bytearray(1024)

prevTime = None

while True:
   now = time.time()
   if (prevTime != None):
      bytesAheadOfSchedule -= ConvertSecondsToBytes(now-prevTime)
   prevTime = now


   print("start to send")
   numBytesSent = sock.sendall(dataBuf)
   #numBytesSent = sock.sendall("hello")
   if (numBytesSent > 0):
      bytesAheadOfSchedule += numBytesSent
      if (bytesAheadOfSchedule > 0):
         time.sleep(ConvertBytesToSeconds(bytesAheadOfSchedule))
   else:
      print "Error sending data, exiting!"
      break

'''
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 50000))
s.sendall('Hello, world')
data = s.recv(1024)
s.close()
print 'Received', repr(data)
'''