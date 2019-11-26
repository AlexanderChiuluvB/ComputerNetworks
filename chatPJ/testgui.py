import tkinter

wuya = tkinter.Tk()
wuya.title("wuya")
wuya.geometry("900x380+300+150")


# add image
pic = r'client/bg.gif'
canvas = tkinter.Canvas(wuya)
image_file = tkinter.PhotoImage(file=pic)
image = canvas.create_image(0,0,anchor='nw',image=image_file)
canvas.place(x=0,y=0,height=360, width=619)

# add lable_title
lp_title = tkinter.Label(wuya,text='舞涯管理系统',font=("Arial Black",22),fg='#32cd99')
lp_title.place(x=625,y=150)

# add copyright_lable
copyright_lable = tkinter.Label(wuya,text='wuya @ copyright')
copyright_lable.pack(side='bottom')

# add name
name_text = tkinter.Variable()
name_lb = tkinter.Label(wuya,text='用户名：',font=('微软雅黑',13))
name_lb.place(x=625,y=200)
name_input = tkinter.Entry(wuya,textvariable=name_text,width=20)
name_input.place(x=685,y=200)

# add password
pwd_text = tkinter.Variable()
pwd_lb = tkinter.Label(wuya,text='密码：',font=('微软雅黑',13))
pwd_lb.place(x=625,y=235)
pwd_input = tkinter.Entry(wuya,width=20,textvariable=pwd_text)
pwd_input.place(x=685,y=235)


# username  and password is real
def login_func():
    if name_text.get() == "":
        msg = "用户名不能为空"
    elif pwd_text.get() == "":
        msg = "密码不能为空"
    elif pwd_text.get()!="" and name_text.get()!="":
        msg = "登陆成功"
    else:
        msg = ""
    pwd_lb = tkinter.Label(wuya,text=msg,font=('微软雅黑',11),fg='red')
    pwd_lb.place(x=685, y=265)


# add login_button
login_button = tkinter.Button(wuya,text='登陆',font=('微软雅黑',12),command=login_func)
login_button.place(x=770,y=280)

# add quit_button
quit_button = tkinter.Button(wuya,text='退出',font=('微软雅黑',12),command=wuya.quit)
quit_button.place(x=700,y=280)

wuya.mainloop()
