import socket

HOST = '127.0.1.1'
 # port to listen(non-privileged is > 1023)
PORT = 9999

#SOCK_STREAM TCP
#SOCK_DGRAM UDP

#create a socket object
#The parameters specify the address family and socket type
#AF_INET IS THE INTERNET address family for IPv4

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:

    #associate the socket with a specfic network interface and port number

    #host can be a hostname or IP address(IPv4) or empty string(accept connections on all
    #available IPv4 interfaces).


    s.bind((HOST,PORT))

    #listen enables a server to accept() connections

    s.listen()

    #accept() when a client connects, it returns a new socket object representing the
    #connection and a tuple holding the address of the client.
    #for IPv4 the tuple will contain (host,port)

    #so conn is a new socket object
    conn,addr = s.accept()

    with conn:
        print("Connected by" ,addr)
        while True:
            #this reads whatever data the client sends
            data = conn.recv(1024)
            if not data:
                break
            #echoes it back
            conn.sendall(data)

