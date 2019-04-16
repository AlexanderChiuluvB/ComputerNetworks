#coding:utf-8
import socket
import datetime
import threading
import struct
import time
import queue as Queue
import random
from collections import deque

"""
定义GLOBAL CONSTANT

"""
#用于存储所有用户的address
all_addr = set()

#key: address value: name of user
user_dict={}

#save the name of all the room
room_list = []

# key: 房间名字 value: 一个存储房间所有用户名字的list
room_user = {}

#保存用户账号密码
user_password = {}

#保存用户在线时间
user_time = {}

#UDP socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = socket.gethostbyname(socket.gethostname())
# server side 与端口 8888绑定
s.bind(('localhost', 8888))

#使用多线程，因此用一个队列来存储server side接受的信息
recvPackets = Queue.Queue()


def recvData(socket,recvPackets):
    """
    把接收到的信息都存储在recvPackets里
    :param socket:
    :param recvPackets:
    :return:
    """
    while True:
        data,addr = socket.recvfrom(1024)
        recvPackets.put((data,addr))


def sendMessage(sock,clientAddr,messType,actionType,data):
    """
    把信息从服务器发送到客户端
    :param sock:
    :param clientAddr:
    :param messType:
    :param actionType:
    :param data:
    :return:
    """
    sendData = str(messType)+str(actionType)+struct.pack('<I',len(data.encode('utf-8')))+data
    sock.sendto(sendData,clientAddr)



def write_to_file(user_password):
    pass

def write_time(user):
    pass

def data_process(data,header,sock,addr):
    """

    :param data:
    :param header:
    :param sock:
    :param addr:
    :return:
    """

    if header == '00':
        #login successful
        index = data.find('@')
        user =  data[:index]
        password = data[index+2:]
        if user in user_password:
            sendMessage(sock,addr,'0','04','用户名已经被注册')
            return
        sendMessage(sock,addr,'0','08','注册成功')
        user_password[user] = password
        write_to_file(user_password)
        write_time(user)

    elif header =='03':
        #用户登录
        index = data.find('@')
        user =  data[:index]
        password = data[index+2:]
        if user not in user_password:
            sendMessage(sock,addr,'0','02','用户不存在')
            return
        if user_password[user]!=password:
            sendMessage(sock,addr,'0','01','密码错误')
            return
        for u in user_dict:
            if user_dict[u] == user:
                sendMessage(sock,u,'0','03','用户已经在线')
                return
        user_time[user] = datetime.datetime.now()
        sendMessage(sock,addr,'0','00','注册成功')
        for u in user_dict:
            if u != user:
                sendMessage(sock,u,'0','05',user)
        user_dict[addr]  =  user
        time.sleep(1)





    elif header =='02':
        #user not exists
        self.client.info = '2'
    elif header == '03':
        #user already online
        self.client.info = '3'
    elif header == '04':
        #username already exists
        self.client.info = '4'
    elif header =='05':
        #user login
        self.client.main_app.all_user.insert(tkinter.END,data)
    elif header == '06':
        #user log out
        self.client.info = '6'
    elif header == '07':
        #create new room
        self.client.main_app.allroom.insert(tkinter.END,data)
    elif header =='08':
        #register successful
        self.client.info ='8'

    elif header =='09':
        #display all online users
        alluser = data.split('#')
        for u in alluser:
            if u != '':
                self.client.main_app.all_user.insert(tkinter.END,data)

    elif header == '10':

        #display all room

        allroom = data.split('#')
        for r in allroom:
            if r != '':
                self.client.main_app.all_room.insert(tkinter.END,r)

    elif header == '11':
        #主页界面信息
        self.client.main_app.HallText.insert(tkinter.END,data)

    elif header =='12':
        #房间信息

        roomIndex = data.find('#')
        roomName = data[0:roomIndex]
        message = data[roomIndex+1:]
        if roomName in self.client.roomList:
            #把信息插入到房间信息界面上
            self.client.roomDict[roomName].main_text.insert(tkinter.END,message)

    elif header =='13':
        #私聊
        userIndex = da


def process(socket,recvPackets):
    """
    处理服务端接收到的信息
    :param socket:
    :param recvPackets:
    :return:
    """
    all_buffer = '' #buffer zone
    single_buffer = '' #接受的单个数据包部分
    flag = False #报头是否得到标识
    header = ''
    supposedLength = 0# 数据部分应该接收的长度
    recvLength = 0 # 当前数据报已经接受的长度

    while True:
        while not recvPackets.empty():
            tmp_data,clientAddr = recvPackets.get()
            all_addr.add(clientAddr)
            all_buffer = all_buffer + tmp_data

            if not tmp_data:
                break

            while True:
                if not flag: #未接收到报头
                    current_len = len(all_buffer)
                    if current_len >=6:

                        header = all_buffer[0:2]
                        supposedLength = (struct.unpack('<I',all_buffer[2:6]))[0]
                        flag = True
                        recvLength = 0
                        all_buffer = all_buffer[6:]
                        single_buffer = ''
                        if len(all_buffer) >= supposedLength: #缓冲区够大
                            single_buffer = all_buffer[:supposedLength]
                            all_buffer = all_buffer[supposedLength:]
                            flag = False #重置为未接收到报头

                            data_process(single_buffer,header,socket,clientAddr)
                            recvLength = 0
                            single_buffer = ''
                            header = ''
                        else: #缓冲区不够大
                            break
                    else:
                        break

                else: #接收到报头

                    tmp_len = supposedLength - recvLength
                    if len(all_buffer) < tmp_len: #缓冲区不够大
                        single_buffer += all_buffer #把所有数据放在单个包中
                        recvLength +=len(all_buffer)
                        all_buffer = '' #reset
                        break

                    else:
                        single_buffer +=all_buffer[0:tmp_len]
                        all_buffer = all_buffer[tmp_len+1:]
                        data_process(single_buffer,header,socket,clientAddr)
                        recvLength = 0
                        single_buffer = ''
                        header = ''
                        flag = False


    #socket.close()






if __name__ == "__main__":

    thread = threading.Thread(target = recvData,args=(s,recvPackets))
    thread.start()
    process(s,recvPackets)



