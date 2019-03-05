from socket import *
from numpy import *
import time

HOST = '127.0.1.1'
PORT = 12000
# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
clientSocket = socket(AF_INET, SOCK_DGRAM)
# Assign IP address and port number to socket
clientSocket.settimeout(1)

for i in range(0,10):
    starttime = time.time()
    message = ('Ping %d %s' % (i+1,starttime)).encode()
    try:
        clientSocket.sendto(message,(HOST,PORT))
        message,addr = clientSocket.recvfrom(1024)
        rtt = time.time()-starttime
        print("%d %s %.8f"%(i+1,HOST,rtt))
    except:
        print('time out for %d'%(i+1))

clientSocket.close()
