#coding:utf-8
from tkinter import *
from tkinter.ttk import *
import socket
import time
import threading
import struct
import tkinter.messagebox
import random

IP = 'localhost'
PORT = 8888

class client:
    def __init__(self,client):
        self.IP = IP
        self.PORT = PORT
        self.connecting = True
        self.client = client
        self.socket = None
        self.ADDR = (self.IP,self.PORT)


    def dataProcess(self,data,header):
        """

        :param data:
        :param header:
        :return:
        """

        """
        下面是header的设计
        """
        if header == '00':
            #login successful
            self.client.info = '0'
        elif header =='01':
            #password wrong
            self.client.info = '1'
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
            userIndex = data.find('#')
            userName = data[0:userIndex]
            message = data[userIndex+1:]

            #如果已经正在私聊
            if self.client.userDict.has_key(userName):
                self.client.userDict[userName].main_text.insert(tkinter.END,message)
            #否则创建新窗口
            else:
                self.client.main_app.new_person = userName
                self.client.main_app.after_idle(self.client.main_app.create_new_user)
                time.sleep(1)
                self.client.userDict[userName].main_text.insert(tkinter.END,message)


    def sendData(self,data_type,action_type,data):
        #报头6个字节
        sendHeader = str(data_type)+str(action_type)+struct.pack('<I',len(data.encode('utf-8')))
        #传送的信息
        sendMessage = sendHeader + data
        #发给服务器
        self.socket.sendto(sendMessage,self.ADDR)


    def recvData(self):
        socket = self.socket

        all_buffer = '' #buffer zone
        single_buffer = '' #接受的单个数据包部分
        flag = False #报头是否得到标识
        header = ''
        supposedLength = 0# 数据部分应该接收的长度
        recvLength = 0 # 当前数据报已经接受的长度

        while self.connecting:
            tmp_data,clientAddr = socket.recvfrom(1024)
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
                            self.dataProcess(single_buffer,header)
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
                        self.dataProcess(single_buffer,header)
                        recvLength = 0
                        single_buffer = ''
                        header = ''
                        flag = False


        socket.close()


    def connect(self):
        if self.socket!=None: #已经连接
            return
        try:
            self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            host = socket.gethostbyname(socket.gethostname())
            port = random.randint(6000,8888) #随机为客户端分配一个端口号
            self.socket.bind((host,port))
        except Exception:
            raise

        self.thread = threading.Thread(target=self.recvData())
        self.thread.start()


    def close(self):
        self.connecting = False
        if self.socket:
            self.socket.shutdown(True)

