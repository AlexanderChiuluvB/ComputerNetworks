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


def readLoginInfo(file):
    """
    读取用户的账号和密码
    :param file:
    :return:
    """
    dict = {}
    #逐行读取

    with open (file,'rb') as f:
        line1 = f.readline()
        while line1!='':
            idx = line1.find('@@')
            dict[line1[0:idx]] = line1[idx+2:len(line1)]
            line1 = f.readline()
    return dict

def write_to_file(user_password):


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

    if header == '注册':
        #login successful
        index = data.find('@@')
        user =  data[:index]
        password = data[index+2:]
        if user in user_password:
            sendMessage(sock,addr,'0','4','用户名已经被注册')
            return
        sendMessage(sock,addr,'0','8','注册成功')
        user_password[user] = password
        write_to_file(user_password)
        write_time(user)

    elif header =='登陆':
        #用户登录
        index = data.find('@@')
        user =  data[:index]
        password = data[index+2:]
        if user not in user_password:
            sendMessage(sock,addr,'0','2','用户不存在')
            return
        if user_password[user]!=password:
            sendMessage(sock,addr,'0','1','密码错误')
            return
        for u in user_dict:
            if user_dict[u] == user:
                sendMessage(sock,u,'0','3','用户已经在线')
                return
        #user_time[user] = datetime.datetime.now()
        sendMessage(sock,addr,'0','0','注册成功')
        for u in user_dict:
            if u != user: #通知其他用户该用户上线了
                sendMessage(sock,u,'0','5',user)
        user_dict[addr] = user
        time.sleep(1)

        online_user = ''
        for u in user_dict:
            online_user += user_dict[u]+'#'
        #剔除最后一个#
        online_user = online_user[0:len(online_user)-1]
        #server side 把 所有在线用户发送给client side
        sendMessage(sock,addr,'0','9',online_user)
        time.sleep(1)

        available_room = ''
        for r in room_list:
            available_room += r + '#'
        # 剔除最后一个#
        available_room = available_room[0:len(available_room) - 1]
        # server side 把 所有房间发送给client side
        sendMessage(sock, addr, '0', 'A', available_room)

    elif header == '新房间':
        #create new room
        room_list.append(data)
        room_user[data] = []
        for c in all_addr:
            sendMessage(sock,c,'0','7',data)

    elif header =='进入房间':

        room_user[data].append(addr)

    elif header =='退出房间':
        if addr in room_user[data]:
            room_user[data].remove(addr)

    elif header == '房间聊天':
        room_name = data[0:data.find('@@')]
        message = data[data.find('@@')+2:]
        for addr in room_user[room_name]:
            #可以在这里添加时间
            sendMessage(sock,addr,'1','2','%s#%s: %s\n' % (room_name,user_dict[addr],message))

    elif header == '私人消息':
        #对方名称
        user_name = data[0:data.find('@@')]
        message = data[data.find('@@')+2:]
        for addr in all_addr:
            if user_dict[addr] == user_name:
                sendMessage(sock,addr,'1','3','%s#%s: %s\n' % (user_name,user_name,message))
                break

    elif header == '大厅信息 ':
        for addr in all_addr:
            sendMessage(sock,addr,'1','1','%s: %s\n' % (user_dict[addr],data))


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

    socket.close()




if __name__ == "__main__":

    user_password = readLoginInfo(r'./loginInfo.txt')
    thread = threading.Thread(target = recvData,args=(s,recvPackets))
    thread.start()
    process(s,recvPackets)



