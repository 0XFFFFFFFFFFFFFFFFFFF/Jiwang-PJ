import socket
import threading
import sys
import Client_ui
from PyQt5.QtWidgets import QApplication, QMainWindow
from functools import partial
from Bidder import *



FINISH_FLAG='1 Leave完成'                #断开客户端连接标识
BUFFER_SIZE=1024                        #一次UDP读取的字节数
PORT=6666                               #服务器端口
MY_BIDDER=Bidder()                      #当前客户端的Bidder变量

app = QApplication(sys.argv)        #Ui界面是主线程，此线程退出则程序整体退出
MainWindow = QMainWindow()
ui = Client_ui.Ui_Server()
ui.setupUi(MainWindow)

client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)  #套接字


def Print_received_msg(ui):
    while MY_BIDDER.is_logined():
        new_msg=client.recv(BUFFER_SIZE)
        new_msg=new_msg.decode('utf-8')
        if new_msg==FINISH_FLAG:        #输入leave命令则关闭当前套接字并退出
            MY_BIDDER.bidder_id=0
            client.close()
            sys.exit(0)
        print(new_msg)
        if len(new_msg)>1 and new_msg[0] in {'0','1'} and new_msg[1]==' ':
            new_msg=new_msg[2:]
        ui.textEdit.append(new_msg)     #服务器返回的命令执行结果打在右侧输出框中


########################################
while not MY_BIDDER.is_logined():       #旋转登陆
    msg='0 '
    msg+=input('>>请登入(命令: login Yourname)')
    client.sendto(msg.encode('utf-8'),('localhost',PORT))
    new_msg,_=client.recvfrom(BUFFER_SIZE)
    new_msg=new_msg.decode('utf-8')
    if new_msg==FINISH_FLAG:
        ui.textEdit.append('您已登出，请关闭界面退出')
        sys.exit(0)
    if new_msg[0]=='0':                 #返回报文首字节是0，说明出错
        continue
    new_msg=new_msg.split(' ')
    if len(new_msg)!=3:
        continue
    MY_BIDDER.bidder_id=int(new_msg[1])
    MY_BIDDER.bidder_name=new_msg[2]
    ui.textEdit.append('您已登入'+'您的ID为：'+str(MY_BIDDER.bidder_id))
########################################

# print('登陆成功')
#线程1在右侧展示从服务器发来的通知消息
T_cmd=threading.Thread(target=Print_received_msg,args=[ui,])
T_cmd.setDaemon(True)
T_cmd.start()


def Sendto_server(ui):
    if MY_BIDDER.is_logined():
        msg=ui.lineEdit.text()      #读入输入框的命令
        ui.lineEdit.setText('')     #清空输入框
        msg=str(MY_BIDDER.bidder_id)+' '+msg#报文开头附上身份标识，这样服务器才知道是哪个客户端发送的请求，以及是否已经登录
        client.sendto(msg.encode('utf-8'),('localhost',PORT))
    else:
        ui.textEdit.setText('您没有登录')
        ui.pushButton.setText('点击这里退出')





#主线程：等待用户输入并将消息发给服务器
ui.pushButton.clicked.connect(partial(Sendto_server,ui))
MainWindow.show()
sys.exit(app.exec_())