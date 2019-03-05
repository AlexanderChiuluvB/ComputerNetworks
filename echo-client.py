import socket


# port to listen(non-privileged is > 1023)
with socket.socket(socket.AF_INET,socket.SOCK_STREAM)as s:
    s.connect(('127.0.1.1',9999))
    #send its message
    s.sendall(b'Hello, world')
    data = s.recv(1024)

#print its received message
print('Received',repr(data))

