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

# key: 房间名字 value: 一个存储房间所有用户address的list
room_user = {}

#保存用户账号密码
user_password = {}

#保存用户在线时间
user_time = {}

#UDP socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = socket.gethostbyname(socket.gethostname())
# server side 与端口 8888绑定
s.bind(('localhost', 8899))

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
    sendData = messType.encode('utf-8')+actionType.encode('utf-8')+struct.pack('<I',len(data))+data.encode('utf-8')
    sock.sendto(sendData,clientAddr)



def write_to_file(user,password):
    with open ('password.txt','a+') as f:
        f.writelines(user+'@@'+password + '\n')

def read_file(file):

    user_password = {}
    with open(file,'r') as f:
        temp_list = f.readlines()
        temp_set = set(temp_list)

        for info in temp_set:
            index = info.find('@@')
            password = info[index+2:]
            user_password[info[:index]] = password[:len(password)-1]

        print(user_password)
        return user_password

def data_process(data,header,sock,client_addr,user_password):

    if header == '01':
        #注册
        index = data.find('@@')
        user =  data[:index]
        password = data[index+2:]

        if user in user_password:

            sendMessage(sock,client_addr,'0','4','用户名已经被注册')

            return

        sendMessage(sock,client_addr,'0','B','注册成功')
        write_to_file(user,password)

    elif header =='03':
        #用户登录
        index = data.find('@@')
        user =  data[:index]
        password = data[index+2:]
        user_password = read_file('password.txt')

        if user not in user_password:
            sendMessage(sock,client_addr,'0','2',u'用户不存在')
            return
        if user_password[user]!=password:
            sendMessage(sock,client_addr,'0','1',u'密码错误')
            return
        for u in user_dict:
            if user_dict[u] == user:
                sendMessage(sock,u,'0','3',u'用户已经在线')
                return
        user_time[user] = datetime.datetime.now()
        sendMessage(sock,client_addr,'0','0',u'用户登录成功')
        for u in all_addr:
            if u != client_addr: #向所有用户告知
                sendMessage(sock,u,'0','5',user)
        user_dict[client_addr]  =  user
        time.sleep(1)

        # send all online user to the currnet user
        online_user = ""
        for u in user_dict:
            online_user = online_user+user_dict[u]+'#'
        online_user = online_user[:len(online_user)-1]
        # 向大厅发送所有在线用户的名字
        sendMessage(sock,client_addr,'0','9',online_user)
        time.sleep(1)

        online_room = ""
        for r in room_list:
            online_room = online_room + r+ '#'
        online_room = online_room[:len(online_room)-1]
        sendMessage(sock,client_addr,'0','A',online_room)

    elif header == '04':
        #进入房间 data 是房间名字


        all_room_user = room_user[data]
        for addr in all_room_user:
            #向房间所有活跃用户发送进入房间的信息
            sendMessage(sock,addr,'1','6',data+'#'+user_dict[client_addr])

        sendData = ''
        room_user[data].append(client_addr)
        sendData +=data
        sendData +='#'
        for u in room_user[data]:
            sendData = sendData + user_dict[u] + '#'
        sendData = sendData[:len(sendData)-1]
        sendMessage(sock,client_addr,'1','4',sendData)


    elif header == '05':
        #退出房间

        #data 房间名
        if client_addr in room_user[data]:
            room_user[data].remove(client_addr)

        print("用户"+user_dict[client_addr]+"退出房间"+data)

        all_room_user = room_user[data]

        for addr in all_room_user:
            #向房间所有活跃用户发送退出房间的信息
            sendMessage(sock,addr,'1','5',user_dict[client_addr])


    elif header =='06':
        # 创建新房间后向所有用户告知
        room_list.append(data)
        room_user[data] = []
        for addr in all_addr:
            sendMessage(sock,addr,'0','7',data)

    elif header =='11' :
        for addr in all_addr:
            sendMessage(sock,addr,'1','1','%s: %s\n' % ( user_dict[client_addr], data))

    elif header =='12' :
        #房间信息
        index = data.find("@@")
        room_name = data[0:index]
        room_mess = data[index+2:]
        for addr in room_user[room_name]:
            sendMessage(sock,addr,'1','2','%s#%s: %s\n' % (room_name,user_dict[client_addr],room_mess))

    elif header == '13': #私人信息

        index = data.find("@@")
        user_name = data[0:index]
        user_mess = data[index+2:]
        for addr in all_addr:
            if user_dict[addr] == user_name:
                sendMessage(sock,addr,'1','3','%s#%s: %s\n' % (user_dict[client_addr], user_dict[client_addr],user_mess))
                break

    elif header =='14': #管理员踢人了

        index = data.find('#')
        room_name = data[:index]
        kick_user = data[index+1:]

        for u in user_dict:
            if user_dict[u] == kick_user:
                kick_addr = u
                room_user[room_name].remove(kick_addr)
                break

        left_addr = room_user[room_name]
        for addr in left_addr:
            sendMessage(sock,addr,'1','5',kick_user)

        #destroy 被踢用户的UI界面
        sendMessage(sock,kick_addr,'1','7',room_name)

    elif header =='15':

        #用户退出登录，告知其他所有在线用户
        for addr in all_addr:
            if user_dict[addr] != data:
                sendMessage(sock,addr,'0','6',data)

def process(socket,recvPackets):
    """
    处理服务端接收到的信息
    :param socket:
    :param recvPackets: Queue 一个队列
    :return:
    """
    all_buffer = '' #buffer zone
    single_buffer =''  #接受的单个数据包部分

    flag = False  #报头是否得到标识
    header = ''

    supposedLength = 0# 数据部分应该接收的长度
    recvLength = 0 # 当前数据报已经接受的长度

    while True:

        while not recvPackets.empty():

            tmp_data,clientAddr = recvPackets.get()

            all_addr.add(clientAddr)

            tmp_data = tmp_data.decode('utf-8')

            print("tmp_data",tmp_data)

            all_buffer = all_buffer + tmp_data

            if not tmp_data:
                break

            while True:
                if not flag: #未接收到报头
                    current_len = len(all_buffer)
                    if current_len >=6:
                        header = all_buffer[0:2]
                        print("header "+header)
                        supposedLength =struct.unpack('<I',all_buffer[2:6].encode('utf-8'))[0]
                        flag = True
                        recvLength = 0
                        all_buffer = all_buffer[6:]
                        single_buffer = ''
                        if len(all_buffer) >= supposedLength: #缓冲区够大
                            single_buffer = all_buffer[:supposedLength]
                            print("single buffer",single_buffer)
                            all_buffer = all_buffer[supposedLength:]
                            flag = False #重置为未接收到报头
                            data_process(single_buffer,header,socket,clientAddr,user_password)
                            recvLength = 0
                            single_buffer = ''
                            header = ''
                        else: #缓冲区不够大
                            break
                    else:
                        break

                else: #接收到报头

                    tmp_len = supposedLength - recvLength
                    if len(all_buffer) < tmp_len: #缓冲区不够大，不能收到完整数据包

                        single_buffer += all_buffer #把所有数据放在单个包中,准备继续接收
                        print("single buffer",single_buffer)
                        recvLength +=len(all_buffer)
                        all_buffer = '' #reset
                        break

                    else: # 已经收到完整数据包
                        single_buffer +=all_buffer[0:tmp_len]
                        print("single buffer",single_buffer)
                        all_buffer = all_buffer[tmp_len+1:]
                        data_process(single_buffer.decode('utf-8'),header,socket,clientAddr,user_password)
                        recvLength = 0
                        single_buffer = ''
                        header = ''
                        flag = False

    socket.close()


def Admin():

    """
    开启服务端后管理员可以在命令行
    进行对聊天室的管理
    :return:
    """
    print("若您是管理员请输入命令")
    while True:
        command = input()
        if command.startswith('/openchannel'):
            roomName = command[13:]
            room_list.append(roomName)
            room_user[roomName] = []
            for addr in all_addr:
                sendMessage(s,addr,'0','7',roomName)

        elif command == '/channels':
            print("所有房间列表")
            for r in room_list:
                print(r)
                print('\n')
        elif command.startswith('/enterchannel'):
            roomName = command[14:]
            print("管理员进入了房间 ",roomName)

            while True:
                adminCommand = input()
                if adminCommand == 'leave':
                    print("管理员退出房间",roomName)
                    break

                elif adminCommand == '/list':
                    print("房间"+roomName+"所有用户")
                    for addr in room_user[roomName]:
                        print(user_dict[addr])

                elif adminCommand.startswith('/kickout'):
                    userid = adminCommand[9:]
                    """
                    kick out
                    """
                    kicked_user_address = ''
                    for addr in user_dict:
                        if user_dict[addr] == userid:
                            kicked_user_address = addr
                            break

                    if(kicked_user_address==''):

                        print("你要踢的用户名字输错了")

                    else:
                        room_user[roomName].remove(kicked_user_address)

                        kick_mess = "用户"+user_dict[kicked_user_address]+"被管理员踢出房间"

                        print(kick_mess)

                        for addr in room_user[roomName]:

                            sendMessage(s,addr,'1','2','%s#%s: %s\n' % (roomName,"管理员",kick_mess))
                else:
                    print("命令输入不正确")

        elif command.startswith('/closechannel'):

            roomName = command[14:]

            for addr in room_user[roomName]:

                sendMessage(s,addr,'1','2','%s#%s: %s\n' % (roomName,"管理员","房间将在5s内被关闭"))

            time.sleep(5)

            room_list.remove(roomName)

            # key: 房间名字 value: 一个存储房间所有用户address的list
            room_user[roomName] = []


        else:
            print("输入命令有误")

if __name__ == "__main__":

    print("服务端正在工作")
    thread = threading.Thread(target = recvData,args=(s,recvPackets))
    thread.start()
    process(s,recvPackets)








