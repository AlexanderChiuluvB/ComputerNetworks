# coding:utf-8
from tkinter import *
from tkinter.ttk import *
import socket
import time
import threading
import struct
import tkinter.messagebox
import tkinter as Tkinter
import random
from gui import LoginApp

IP = 'localhost'
PORT = 8888


class client:

    def __init__(self, p=None):
        self.IP = IP
        self.PORT = PORT
        self.flag = True
        self.connecting = True
        self.client = p
        self.socket = None
        self.ADDR = (self.IP, self.PORT)

    def dataProcess(self, data, header):
        """

        :param data:
        :param header:
        :return:
        """

        """
        下面是header的设计
        
        """

        print("data:" + data)

        if header == '00':
            # login successful
            self.client.stop_flag = '0'
        elif header == '01':
            # password wrong
            self.client.stop_flag = '1'
        elif header == '02':
            # user not exists
            self.client.stop_flag = '2'
        elif header == '03':
            # user already online
            self.client.stop_flag = '3'

        elif header == '04':
            # username already exists
            self.client.stop_flag = '4'

        elif header == '05':
            # 用户登录
            self.client.main_app.all_player.insert(Tkinter.END, data)
            print("用户登录" + data)

        elif header == '06':
            # 用户退出大厅
            print("用户退出" + data)
            for i in range(self.client.main_app.all_player.size()):  # 删除退出用户
                if self.client.main_app.all_player.get(i) == data:
                    print(self.client.main_app.all_player.get(i))
                    self.client.main_app.all_player.delete(i)
                    break

        elif header == '07':
            # 创建新房间
            print("创建新房间" + data)
            self.client.main_app.allroom.insert(tkinter.END, data)

        elif header == '0B':
            # register successful
            self.client.stop_flag = 'B'

        elif header == '09':
            # 在大厅里展示所有的在线用户
            alluser = data.split('#')
            for u in alluser:
                if u != '':
                    self.client.main_app.all_player.insert(tkinter.END, u)

        elif header == '0A':
            # display all room
            allroom = data.split('#')
            for r in allroom:
                if r != '':
                    print(r)
                    self.client.main_app.allroom.insert(tkinter.END, r)

        elif header == '11':
            # 大厅信息
            print("大厅信息" + data)
            self.client.main_app.datingtext.insert(tkinter.END, data)

        elif header == '12':
            # 房间信息
            roomIndex = data.find('#')
            roomName = data[0:roomIndex]
            message = data[roomIndex + 1:]
            if roomName in self.client.room_app:
                # 把信息插入到房间信息界面上
                self.client.room_app[roomName].main_text.insert(tkinter.END, message)


        elif header == '13':
            # 私聊
            userIndex = data.find('#')
            userName = data[0:userIndex]
            message = data[userIndex + 1:]

            # 如果已经正在私聊
            if userName in self.client.person_app:
                self.client.person_app[userName].main_text.insert(tkinter.END, message)
            # 否则创建新窗口
            else:
                self.client.main_app.new_person = userName
                self.client.main_app.after_idle(self.client.main_app.create_new_person)
                time.sleep(1)
                self.client.person_app[userName].main_text.insert(tkinter.END, message)

        elif header == '14':
            # 这里的data是房间内所有用户的名称
            roomIndex = data.find('#')
            roomName = data[0:roomIndex]
            alluserdata = data[roomIndex + 1:]
            alluser = alluserdata.split('#')
            for u in alluser:
                if u != '':
                    self.client.room_app[roomName].all_room_user.insert(tkinter.END, u)


        elif header == '15':
            # 用户退出房间
            # data 是 用户名
            for i in range(self.client.room_user.size()):  # 删除退出用户
                if self.client.room_user.get(i) == data:
                    self.client.room_user.delete(i)
                    break

        elif header == '16':

            index = data.find('#')
            roomName = data[0:index]
            newUser = data[index + 1:]
            self.client.room_app[roomName].all_room_user.insert(tkinter.END, newUser)


        elif header == '17':
            self.client.room_pointer.master.destroy()

    def sendData(self, data_type, action_type, data):

        sendMessage = data_type.encode('utf-8') + action_type.encode('utf-8') + struct.pack('<I',
                                                                                            len(data)) + data.encode(
            'utf-8')

        # 发给服务器
        self.socket.sendto(sendMessage, self.ADDR)

    def recvData(self):
        socket = self.socket

        all_buffer = ''  # buffer zone
        single_buffer = ''  # 接受的单个数据包部分
        flag = False  # 报头是否得到标识
        header = ''
        supposedLength = 0  # 数据部分应该接收的长度
        recvLength = 0  # 当前数据报已经接受的长度

        while self.connecting:
            tmp_data, clientAddr = socket.recvfrom(1024)
            tmp_data = tmp_data.decode('utf-8')
            print("tmp_data" + tmp_data)
            all_buffer = all_buffer + tmp_data
            if not tmp_data:
                break
            while True:
                if not flag:  # 未接收到报头
                    current_len = len(all_buffer)
                    if current_len >= 6:
                        header = all_buffer[:2]
                        print(header)
                        print("all_buffer", all_buffer)
                        supposedLength = struct.unpack('<I', all_buffer[2:6].encode('utf-8'))[0]
                        flag = True
                        recvLength = 0
                        all_buffer = all_buffer[6:]
                        single_buffer = ''
                        if len(all_buffer) >= supposedLength:  # 缓冲区够大

                            single_buffer = all_buffer[:supposedLength]

                            all_buffer = all_buffer[supposedLength:]
                            flag = False  # 重置为未接收到报头
                            self.dataProcess(single_buffer, header)
                            recvLength = 0
                            single_buffer = ''
                            header = ''
                        else:  # 缓冲区不够大
                            break
                    else:
                        break

                else:  # 接收到报头

                    tmp_len = supposedLength - recvLength
                    if len(all_buffer) < tmp_len:  # 缓冲区不够大
                        single_buffer += all_buffer  # 把所有数据放在单个包中
                        recvLength += len(all_buffer)
                        all_buffer = ''  # reset
                        break

                    else:
                        single_buffer += all_buffer[0:tmp_len]
                        all_buffer = all_buffer[tmp_len + 1:]
                        self.dataProcess(single_buffer, header)
                        recvLength = 0
                        single_buffer = ''
                        header = ''
                        flag = False

    def connect(self):
        if self.socket != None:  # 已经连接
            return
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # host = socket.gethostbyname(socket.gethostname())
            host = 'localhost'
            port = random.randint(6000, 8887)  # 随机为客户端分配一个端口号
            print((host, port))
            self.socket.bind((host, port))
        except Exception:
            raise

        self.thread = threading.Thread(target=self.recvData)
        self.thread.start()

    def bind_text(self, app):
        self.text = app

    def close(self):
        self.connecting = False
        if self.socket:
            self.socket.shutdown(True)


class App:

    def __init__(self):
        self.sock = client(p=self)
        self.gui = LoginApp(clientp=self)
        self.text = None
        self.info = None
        self.main_app = None  # 大厅界面pointer
        self.room_app = {}
        self.person_app = {}
        self.room_user = None
        self.room_pointer = None  # 聊天室界面pointer
        self.stop_flag = None  # 停止标志

    def change_gui(self, gui=None):
        self.gui = None
        self.gui = gui

    def show(self):
        self.gui.mainloop()

    def close(self):
        self.gui.quit()


if __name__ == '__main__':
    try:
        app = App()
        app.show()
    except Exception:
        raise
