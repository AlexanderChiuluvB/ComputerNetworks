from socket import *

serverSocket = socket(AF_INET,SOCK_STREAM)

serverSocket.bind(('127.0.1.1',12003))

#maximum connection number is 1
serverSocket.listen(1)


while True:
    conn,addr = serverSocket.accept()

    try:
        data = conn.recv(1024)
        filename = data.split()[1]
        f = open(filename[1:])
        outputdata = f.read()
        #send one HTTP header into socket
        header = ' HTTP/1.1 200 OK\nConnection: close\nContent-Type: text/html\nContent-Length: %d\n\n' % (len(outputdata))
        conn.send(header.encode())
        print(len(outputdata))
        for i in range(len(outputdata)):
            conn.send(outputdata[i].encode())
        conn.close()
    except:
        header = 'HTTP/1.1 404 Found'
        conn.send(header.encode())
        conn.close()

serverSocket.close()
