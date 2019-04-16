#coding:utf-8
import socket
import time
import datetime
import threading
import struct
import sys
import Queue
import random
from collections import deque
reload(sys)
sys.setdefaultencoding('utf-8')
all_addr = set()

def send_mess(mess_type,action_type,str_mess,sock,clientaddr):
    send_len = str_mess.encode('utf-8')
    send_data = str(mess_type) + str(action_type) + struct.pack('<I', len(send_len)) + str_mess  # 长度为固定四个字节，也就是报头为6个字节
    sock.sendto(send_data,clientaddr)

def body_process(one_buffer,head_str,sock,clientaddr):
    global all_socket
    global all_user
    global all_room
    global room_user
    global user_pwd
    global num_game
    if head_str == '01': # 注册用户
        index = one_buffer.find('@@')
        print '用户:' + one_buffer[0:index] + '创建...'  # 用户名
        print one_buffer[index + 2:]  # 密码
        if user_pwd.has_key(one_buffer[0:index]):
            send_mess('0', '4', u'用户名已被注册', sock,clientaddr)
            return
        send_mess('0', 'B', u'注册成功', sock,clientaddr)
        user_pwd[one_buffer[0:index]] = one_buffer[index + 2:]  # 创建新用户
        write_file(user_pwd)
        write_time(one_buffer[0:index])  # 计入新用户
    elif head_str == '03':  # 用户登陆
        index = one_buffer.find('@@')
        if not user_pwd.has_key(one_buffer[0:index]):  # 用户不存在
            send_mess('0','2',u'用户不存在',sock,clientaddr)
            return
        print '用户:' + one_buffer[0:index] + '登录...'  # 用户名
        print one_buffer[index + 2:]  # 密码
        if user_pwd[one_buffer[0:index]] != one_buffer[index + 2:]:
            send_mess('0', '1', u'密码错误', sock,clientaddr)
            return
        for c in all_user:
            if all_user[c] == one_buffer[0:index]:
                send_mess('0', '3', u'用户已在线', sock,c)
                return
        user_time[one_buffer[0:index]] = datetime.datetime.now()   # 记录开始登录时间
        send_mess('0', '0', u'用户登录成功', sock,clientaddr)
        for c in all_addr:  # 向所有用户告知
            if c!=clientaddr:
                send_mess('0', '5',one_buffer[0:index],sock,c)
        all_user[clientaddr] = one_buffer[0:index]
        time.sleep(1)
        mess_user = ''
        for c in all_user:
            mess_user = mess_user + all_user[c] + '#'
        mess_user = mess_user[0:len(mess_user) - 1]
        send_mess('0','9',mess_user,sock,clientaddr)  # 发送在线用户
        time.sleep(1)
        mess_room = ''
        for r in all_room:
            mess_room = mess_room + r + '#'
        mess_room = mess_room[0:len(mess_room) - 1]
        send_mess('0', 'A', mess_room, sock,clientaddr)  # 发送房间

    elif head_str == '06':  # 创建新房间
        print '创建新房间:' + one_buffer
        all_room.append(one_buffer)
        room_user[one_buffer] = []
        room_answer[one_buffer] = [] # 在回答字典中加入该key
        answer_valid[one_buffer] = False # 该房间是否处于接收答案状态
        num_game[one_buffer] = []   # 存储房间游戏数字
        t = threading.Thread(target=game_process,args=(one_buffer,))
        t.setDaemon(True)
        t.start()
        for c in all_addr:  # 向所有用户告知
            send_mess('0', '7',one_buffer,sock,c)

    elif head_str == '04':  # 进入房间
        room_user[one_buffer].append(clientaddr)
        print '用户' + all_user[clientaddr] + '进入房间' + one_buffer

    elif head_str == '05':  # 退出房间
        if clientaddr in room_user[one_buffer]:
            room_user[one_buffer].remove(clientaddr)
        print '用户' + all_user[clientaddr] + '退出房间' + one_buffer
    elif head_str == '10': # 游戏答案
        tmp_room_name = one_buffer[0:one_buffer.find('@@')]
        tmp_ans = one_buffer[one_buffer.find('@@') + 2:]
        send_name = all_user[clientaddr]  # 发答案的用户
        valid_char = ['*','-','+','/','(',')']
        ans = []
        tmp_res = ''
        for ch in tmp_ans:
            if ch not in valid_char: # 判断是否作弊
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
            eval(tmp_ans) # 判断答案是否有效
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
        for addr in room_user[tmp_room_name]:
            #u.send('%s--%s\n' % (all_user[sock], tmp_mess))
            send_mess('1','2','%s#%s: %s\n' % (tmp_room_name,all_user[clientaddr], tmp_mess),sock,addr)   # #号前面是房间名称
    elif head_str == '13':  # 私人消息
        tmp_user_name = one_buffer[0:one_buffer.find('@@')]  # 私人消息对方名称
        tmp_mess = one_buffer[one_buffer.find('@@') + 2:]  # 私人消息内容
        for addr in all_addr:
            if all_user[addr] == tmp_user_name:
                #u.send('%s--%s\n' % (all_user[sock], tmp_mess))
                send_mess('1', '3', '%s#%s: %s\n' % (all_user[clientaddr], all_user[clientaddr], tmp_mess), sock,addr)
                break
    elif head_str == '11':  # 大厅消息
        for addr in all_addr:
            #u.send('%s--%s\n' % (all_user[sock], one_buffer))
            send_mess('1', '1', '%s: %s\n' % ( all_user[clientaddr], one_buffer), sock,addr)

####################################################################################

def chat_process(sock,recvPackets):

    global all_socket
    global all_user
    global all_room
    global room_user
    all_buffer = '' # 该套接字接收缓冲区
    one_buffer = '' # 该套接字正在接收的单个数据包部分
    flag = False    # 报头已得到标识
    head_str = ''   # 报头的字符串表示
    data_body_len = 0    # 此数据报数据部分应该接受的长度
    recive_len = 0  # 当前数据报已收到的长度
    while True:
        #client addr
        while not recvPackets.empty():
            tmp_buffer,clientaddr =recvPackets.get() # 本次获取的数据
            #if clientaddr not in all_addr:
              #  all_addr.add(clientaddr)
             #   continue
            all_addr.add(clientaddr)
            print "tmp buffer"+ tmp_buffer
            all_buffer = all_buffer + tmp_buffer
            if not tmp_buffer:
                break
            while True:
                if flag:  # 如果已得到报头
                    tmp_len = data_body_len - recive_len
                    if len(all_buffer) < tmp_len:  # 不能收到完整数据包
                        one_buffer += all_buffer  # 将所有数据放到单个包里,准备继续接收
                        recive_len += len(all_buffer)  # 改变已接受长度
                        all_buffer = ''  # 清空接收缓冲区
                        break
                    else:  # 已经收到完整数据包
                        one_buffer += all_buffer[0:tmp_len]
                        all_buffer = all_buffer[tmp_len + 1:]  # 清空已经放到单个包的缓冲区数据
                        ###
                        # 处理
                        body_process(one_buffer,head_str,sock,clientaddr)
                        ###
                        flag = False  # 变成未接收到报头
                        one_buffer = ''  # 清空单包数据
                        head_str = ''
                        recive_len = 0  # 清空长度
                else:  # 未接收到报头
                    all_len = len(all_buffer)  # 当前已经有的数据包长度
                    if all_len >= 6:
                        head_str = all_buffer[0:2]  # 头部表示
                        data_body_len = (struct.unpack('<I', all_buffer[2:6]))[0]
                        flag = True
                        recive_len = 0
                        all_buffer = all_buffer[6:]
                        one_buffer = ''
                        if len(all_buffer) >= data_body_len:
                            one_buffer = all_buffer[:data_body_len]
                            all_buffer = all_buffer[data_body_len:]
                            ###
                            # 处理
                            body_process(one_buffer,head_str,sock,clientaddr)
                            flag = False  # 变成未接收到报头
                            one_buffer = ''  # 清空单包数据
                            head_str = ''
                            recive_len = 0  # 清空长度
                        else:
                            break
                    else:
                        break
    ###############################################
    sock.close()
    """
    all_socket.remove(sock)
    quit_name = ''
    for r in room_user:  # 删除所在房间
        if sock in room_user[r]:
            room_user[r].remove(sock)
    if all_user.has_key(sock):
        print '用户:' + all_user[sock] + '退出登录...'
        update_time(user_time,all_user[sock])  # 记录该用户在线时长
        quit_name = all_user[sock]
        all_user.pop(sock)
        user_time.pop(quit_name)  # 删除退出用户时长
    for u in all_user:
        send_mess('0','6',quit_name,u,clientaddr)  # 发送退出消息
    #print 'Connection from %s:%s closed.' % addr
    """
################################################
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
#Server Code

def RecvData(sock,recvPackets):
    while True:
        data,addr = sock.recvfrom(1024)
        recvPackets.put((data,addr))

#########################################################################
############主程序开始
######################################################################
user_time_path = r'./online_time.txt'  # 配置存储用户在线时间目录
user_pwd_path = r'./server_user.txt' # 配置用户密码信息目录
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = socket.gethostbyname(socket.gethostname())
s.bind(('localhost', 5558))
#s.listen(5)
user_time = {}   # key为用户名 value 为在线时间  格式  wen@@3600     后面为秒数
user_pwd = read_file(user_pwd_path)  # 从文件读取用户信息
print user_pwd
all_socket = []   # 所有套接字列表
all_user = {}    # key为套接字 value 为用户名
all_room = []   # key 房间名 
room_user = {}  # key 房间名 value 该房间所有用户, 是一个list
room_answer = {} # key 房间名 value 是一个[u1 ,ans_str]  第一个key是回答的用户，第二个是回答串
#answer_valid = {} # key 房间名 value为当前回答是否有效, 就是是否在15秒之内被服务器收到
#num_game = {} # key为房间名  value为list （当前21点游戏四个数字）
recvPackets = Queue.Queue()
t = threading.Thread(target = RecvData,args=(s,recvPackets))
t.start()
chat_process(s,recvPackets)

