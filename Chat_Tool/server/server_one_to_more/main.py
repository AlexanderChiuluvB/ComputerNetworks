#coding:utf-8
import socket, select
import random
import time
import datetime
import threading
import struct
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

class Chat_One_Process():

   def __init__(self,sock,addr):     # 接收到一个连接请求后，生成一个该对象,该对象存储该连接用户的所有信息
      self.all_buffer = ''  # 该套接字接收缓冲区
      self.one_buffer = ''  # 该套接字正在接收的单个数据包部分
      self.flag = False  # 报头已得到标识
      self.head_str = ''  # 报头的字符串表示
      self.data_body_len = 0  # 此数据报数据部分应该接受的长度
      self.recive_len = 0  # 当前数据报已收到的长度
      self.sock = sock  # 该对象处理的套接字
      self.addr = addr  # 该对象处理对象的地址

   def game_process(self,room_name):  # 处理每个房间游戏题目的发放和胜利玩家提示
      global room_answer
      global answer_valid
      global num_game
      global room_user
      while True:
         while int(datetime.datetime.now().second) % 30 != 0:  # 每半分钟一个题目
            time.sleep(1)
         print int(datetime.datetime.now().second)
         tmp_mess = '21点游戏开始...(请在20秒之内回答,用下面四个数运算成最接近21的玩家胜利)\n数字:'
         num_game[room_name] = ['1', '2', '3', '4']
         num_game[room_name][0] = str(random.randint(1, 10))
         num_game[room_name][1] = str(random.randint(1, 10))
         num_game[room_name][2] = str(random.randint(1, 10))
         num_game[room_name][3] = str(random.randint(1, 10))
         tmp_mess = tmp_mess + num_game[room_name][0] + '  '
         tmp_mess = tmp_mess + num_game[room_name][1] + '  '
         tmp_mess = tmp_mess + num_game[room_name][2] + '  '
         tmp_mess = tmp_mess + num_game[room_name][3] + '  '
         for u in room_user[room_name]:
            self.send_mess('1', '2', '%s#%s: %s\n' % (room_name, '服务器消息', tmp_mess), u)  # #号前面是房间名称
         answer_valid[room_name] = True
         time.sleep(20)  # 等待玩家回答
         answer_valid[room_name] = False  # 关闭接收答案
         if room_answer[room_name] != []:  # 有回答
            for u in room_user[room_name]:
               tmp_mess = '胜利玩家:' + room_answer[room_name][0] + '\n' + '回答:' + room_answer[room_name][1] + ' = ' + str(
                  eval(room_answer[room_name][1])) + '......'
               self.send_mess('1', '2', '%s#%s: %s\n' % (room_name, '服务器消息', tmp_mess), u)  # #号前面是房间名称
         else:
            tmp_mess = '无人回答,本局无人胜利'
            for u in room_user[room_name]:
               self.send_mess('1', '2', '%s#%s: %s\n' % (room_name, '服务器消息', tmp_mess), u)  # #号前面是房间名称
         room_answer[room_name] = []  # 清除回答
         num_game[room_name] = []

   def send_mess(self, mess_type, action_type, str_mess, sock):

      global mess_queue
      send_len = str_mess.encode('utf-8')
      send_data = str(mess_type) + str(action_type) + struct.pack('<I',
                                                                  len(send_len)) + str_mess  # 长度为固定四个字节，也就是报头为6个字节
      mess_queue[sock].append(send_data)   # 加入发送队列
      #sock.send(send_data)
      
   def body_process(self,one_buffer, head_str, sock):
      global all_socket
      global all_user
      global all_room
      global room_user
      global user_pwd
      global num_game
      #if head_str !='03' and (not all_user.has_key(sock)): # 防止未登录发消息
      #  return
      if head_str == '01':  # 注册用户
         index = one_buffer.find('@@')
         print '用户:' + one_buffer[0:index] + '创建...'  # 用户名
         print one_buffer[index + 2:]  # 密码
         if user_pwd.has_key(one_buffer[0:index]):
            self.send_mess('0', '4', u'用户名已被注册', sock)
            return
         self.send_mess('0', 'B', u'注册成功', sock)
         user_pwd[one_buffer[0:index]] = one_buffer[index + 2:]  # 创建新用户
         write_file(user_pwd)
         write_time(one_buffer[0:index])  # 计入新用户
      elif head_str == '03':  # 用户登陆
         index = one_buffer.find('@@')
         if not user_pwd.has_key(one_buffer[0:index]):  # 用户不存在
            self.send_mess('0', '2', u'用户不存在', sock)
            return
         print '用户:' + one_buffer[0:index] + '登录...'  # 用户名
         print one_buffer[index + 2:]  # 密码
         if user_pwd[one_buffer[0:index]] != one_buffer[index + 2:]:
            self.send_mess('0', '1', u'密码错误', sock)
            return
         for u in all_user:
            if all_user[u] == one_buffer[0:index]:
               self.send_mess('0', '3', u'用户已在线', sock)
               return
         user_time[one_buffer[0:index]] = datetime.datetime.now()  # 记录开始登录时间
         self.send_mess('0', '0', u'用户登录成功', sock)
         for u in all_user:  # 向所有用户告知
            self.send_mess('0', '5', one_buffer[0:index], u)
         all_user[sock] = one_buffer[0:index]
         mess_user = ''
         for u in all_user:
            mess_user = mess_user + all_user[u] + '#'
         mess_user = mess_user[0:len(mess_user) - 1]
         self.send_mess('0', '9', mess_user, sock)  # 发送在线用户
         time.sleep(1)
         mess_room = ''
         for r in all_room:
            mess_room = mess_room + r + '#'
         mess_room = mess_room[0:len(mess_room) - 1]
         self.send_mess('0', 'A', mess_room, sock)  # 发送房间

      elif head_str == '06':  # 创建新房间
         print '创建新房间:' + one_buffer
         all_room.append(one_buffer)
         room_user[one_buffer] = []
         room_answer[one_buffer] = []  # 在回答字典中加入该key
         answer_valid[one_buffer] = False  # 该房间是否处于接收答案状态
         num_game[one_buffer] = []  # 存储房间游戏数字
         t = threading.Thread(target=self.game_process, args=(one_buffer,))
         t.setDaemon(True)
         t.start()
         for u in all_user:  # 向所有用户告知
            self.send_mess('0', '7', one_buffer, u)

      elif head_str == '04':  # 进入房间
         room_user[one_buffer].append(sock)
         print '用户' + all_user[sock] + '进入房间' + one_buffer
      elif head_str == '05':  # 退出房间
         if sock in room_user[one_buffer]:
            room_user[one_buffer].remove(sock)
         print '用户' + all_user[sock] + '退出房间' + one_buffer
      elif head_str == '10':  # 游戏答案
         tmp_room_name = one_buffer[0:one_buffer.find('@@')]
         tmp_ans = one_buffer[one_buffer.find('@@') + 2:]
         send_name = all_user[sock]  # 发答案的用户
         valid_char = ['*', '-', '+', '/', '(', ')']
         ans = []
         tmp_res = ''
         for ch in tmp_ans:
            if ch not in valid_char:  # 判断是否作弊
               tmp_res = tmp_res + ch
            else:
               if tmp_res != '':
                  ans.append(tmp_res)
                  tmp_res = ''
         if tmp_res != '':
            ans.append(tmp_res)

         if answer_valid[tmp_room_name] == False:  # 不可以接受答案
            return

         if set(ans) != set(num_game[tmp_room_name]):  # 判断是否合法数字
            return

         print '游戏:'
         print num_game[tmp_room_name]
         print '回答:'
         print ans

         try:
            eval(tmp_ans)  # 判断答案是否有效
         except Exception:
            return

         if eval(tmp_ans) > 21:
            return
         if room_answer[tmp_room_name] == []:  # 还无人回答
            room_answer[tmp_room_name] = [send_name, tmp_ans]
         else:
            if abs(eval(room_answer[tmp_room_name][1]) - 21) > abs(eval(tmp_ans) - 21):  # 找到更好的答案
               room_answer[tmp_room_name] = [send_name, tmp_ans]

      #####################################################################################
      elif head_str == '12':  # 房间消息
         tmp_room_name = one_buffer[0:one_buffer.find('@@')]  # 房间名称
         tmp_mess = one_buffer[one_buffer.find('@@') + 2:]  # 房间消息
         for u in room_user[tmp_room_name]:
            # u.send('%s--%s\n' % (all_user[sock], tmp_mess))
            self.send_mess('1', '2', '%s#%s: %s\n' % (tmp_room_name, all_user[sock], tmp_mess), u)  # #号前面是房间名称
      elif head_str == '13':  # 私人消息
         tmp_user_name = one_buffer[0:one_buffer.find('@@')]  # 私人消息对方名称
         tmp_mess = one_buffer[one_buffer.find('@@') + 2:]  # 私人消息内容
         for u in all_socket:
            if all_user[u] == tmp_user_name:
               # u.send('%s--%s\n' % (all_user[sock], tmp_mess))
               self.send_mess('1', '3', '%s#%s: %s\n' % (all_user[sock], all_user[sock], tmp_mess), u)
               break
      elif head_str == '11':  # 大厅消息
         for u in all_user:
            # u.send('%s--%s\n' % (all_user[sock], one_buffer))
            self.send_mess('1', '1', '%s: %s\n' % (all_user[sock], one_buffer), u)

   ####################################################################################
   def clear_process(self):
      quit_name = ''
      for r in room_user:  # 删除所在房间
         if self.sock in room_user[r]:
            room_user[r].remove(self.sock)
      if all_user.has_key(self.sock):
         print '用户:' + all_user[self.sock] + '退出登录...'
         update_time(user_time, all_user[self.sock])  # 记录该用户在线时长
         quit_name = all_user[self.sock]
         all_user.pop(self.sock)
         user_time.pop(quit_name)  # 删除退出用户时长
      for u in all_user:
         self.send_mess('0', '6', quit_name, u)  # 发送退出消息
      print 'Connection from %s:%s closed.' % self.addr

   def mess_process(self):  # 消息处理，当套接字可读时，调用该函数
      global mess_queue

      tmp_buffer = self.sock.recv(1024)  # 本次获取的数据
      self.all_buffer = self.all_buffer + tmp_buffer
      if not tmp_buffer:  #  对方关闭连接
         mess_queue.pop(self.sock)  # 清除消息队列
         self.sock.close()
         if self.sock in all_socket:
            all_socket.remove(self.sock)
         self.clear_process()
         return

      while True:
         if self.flag:  # 如果已得到报头
            tmp_len = self.data_body_len - self.recive_len
            if len(self.all_buffer) < tmp_len:  # 不能收到完整数据包
               self.one_buffer += self.all_buffer  # 将所有数据放到单个包里,准备继续接收
               self.recive_len += len(self.all_buffer)  # 改变已接受长度
               self.all_buffer = ''  # 清空接收缓冲区
               break
            else:  # 已经收到完整数据包
               self.one_buffer += self.all_buffer[0:tmp_len]
               self.all_buffer = self.all_buffer[tmp_len + 1:]  # 清空已经放到单个包的缓冲区数据
               ###
               # 处理
               self.body_process(self.one_buffer, self.head_str, self.sock)
               ###
               self.flag = False  # 变成未接收到报头
               self.one_buffer = ''  # 清空单包数据
               self.head_str = ''
               self.recive_len = 0  # 清空长度
         else:  # 未接收到报头
            all_len = len(self.all_buffer)  # 当前已经有的数据包长度
            if all_len >= 6:
               self.head_str = self.all_buffer[0:2]  # 头部表示
               self.data_body_len = (struct.unpack('<I', self.all_buffer[2:6]))[0]
               self.flag = True
               self.recive_len = 0
               self.all_buffer = self.all_buffer[6:]
               self.one_buffer = ''
               if len(self.all_buffer) >= self.data_body_len:
                  self.one_buffer = self.all_buffer[:self.data_body_len]
                  self.all_buffer = self.all_buffer[self.data_body_len:]
                  ###
                  # 处理
                  self.body_process(self.one_buffer, self.head_str, self.sock)
                  self.flag = False  # 变成未接收到报头
                  self.one_buffer = ''  # 清空单包数据
                  self.head_str = ''
                  self.recive_len = 0  # 清空长度
               else:
                  break
            else:
               break

class MyThread(threading.Thread):

   def __init__(self):
      threading.Thread.__init__(self)
      self.func = self.listen_mess
      self.chat_users = {}  # sock:chat-one
      self.mess_input = [] # 该线程处理的所有套接字

   def run(self):
      apply(self.listen_mess,())

   def user_append(self,sock,addr):
      per = Chat_One_Process(sock,addr)  # 加一个处理对象
      self.chat_users[sock] = per
      self.mess_input.append(sock)

   def listen_mess(self):

      global mess_queue

      while True:
         while self.mess_input == []:
            pass
         rs, ws, es = select.select(self.mess_input, self.mess_input, [])
         for sockno in rs:
            self.chat_users[sockno].mess_process()
            if not mess_queue.has_key(sockno):
               self.mess_input.remove(sockno)
               self.chat_users.pop(sockno)
         for sockno in ws:
            if mess_queue.has_key(sockno) and len(mess_queue[sockno]) > 0:
               ret = sockno.send(mess_queue[sockno][0])       # 写一个消息给客户端
               if ret == -1:   # 套接字错误
                  sockno.shutdown(True)
                  if sockno in all_socket:
                     all_socket.remove(sockno)
                  for ss in self.chat_users:
                     if ss == sockno:
                        self.chat_users[ss].clear_process()
                     self.mess_input.remove(sockno)
                     self.chat_users.pop(sockno)
                ###############################################################################
               if mess_queue[sockno][0].find('用户登录成功') != -1:
                  time.sleep(1)
               mess_queue[sockno].pop(0)


def write_file(user):
    f = open(user_pwd_path,'w')
    for u in user:
      f.write(u + '@@' + user[u] + '\n')
    f.close()

def update_time(user_time,user_name):
    total_time = (datetime.datetime.now() - user_time[user_name]).seconds  # 在线时长
    print 'total_time:' + str(total_time)
    f = open(user_time_path, 'r')
    lines = f.readlines()
    index = 0
    for line in lines:
        if user_name == line[0:line.find('@@')]:
            per_time = eval(line[line.find('@@') + 2:])
            total_time = per_time + total_time
            tmp_line = user_name + '@@' + str(total_time) + '\n'
            lines[index] = tmp_line
            break
        index = index + 1
    f.close()
    f = open(user_time_path, 'w')
    for line in lines:
        f.write(line)
    f.close()
    return

def write_time(user_name):
    f = open(user_time_path, 'a')
    f.write(user_name + '@@0\n' )
    f.close()

def read_file(str):
    f = open(str, 'r')
    ret = {}
    line_one = f.readline()
    while line_one != '':
        index = line_one.find('@@')
        ret[line_one[0:index]] = line_one[index + 2:len(line_one) - 1]
        line_one = f.readline()
    f.close()
    return ret

user_time_path = r'./online_time.txt'  # 配置存储用户在线时间目录
user_pwd_path = r'./server_user.txt' # 配置用户密码信息目录
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('0.0.0.0', 5556))
user_time = {}   # key为用户名 value 为在线时间  格式  wen@@3600     后面为秒数
user_pwd = read_file(user_pwd_path)  # 从文件读取用户信息
print user_pwd
all_socket = []   # 所有套接字列表
all_user = {}    # key为套接字 value 为用户名
all_room = []   # key 房间名
mess_queue = {}  # key 为套接字, value为发送列表[mess1,mess2]
room_user = {}  # key 房间名 value 该房间所有用户, 是一个list
room_answer = {} # key 房间名 value 是一个[u1 ,ans_str]  第一个key是回答的用户，第二个是回答串
answer_valid = {} # key 房间名 value为当前回答是否有效, 就是是否在15秒之内被服务器收到
num_game = {} # key为房间名  value为list （当前21点游戏四个数字)
threads = []
for i in range(100):
   threads.append(MyThread())
   threads[i].start()
index = 0
while True:
    while len(all_socket) > 10000:  #最多接受10000用户在线
         time.sleep(1)
    sock,addr = s.accept()
    all_socket.append(sock)   # 新来一个用户
    sock.setblocking(0)   # 设置非阻塞
    print '当前服务器用户数目: ' + str(len(all_socket))
    mess_queue[sock] = []
    print '该用户加入线程:' + str(index) + ' .....'
    while len(threads[index].mess_input) > 200:  # 当单个线程处理超过200用户时, 不再添加用户
       index = (index + 1) % 10
    threads[index].user_append(sock,addr)







