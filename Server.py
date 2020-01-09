import threading
import socket
import socketserver
import sys
import Server_ui
from PyQt5.QtWidgets import QApplication, QMainWindow
from functools import partial
from Auction import *
from Bidder import *



#每个竞拍者拥有各自的客户端程序，所有客户端连接到同一个服务端。
FINISH_FLAG='1 Leave完成'                #断开客户端连接标识
BUFFER_SIZE=1024                        #一次UDP读取的字节数
HOST='localhost'                        #主机IP 
PORT=6666                               #服务器端口
ADDRESS=(HOST,PORT)                     #主机地址
MOST_BIDDERS=100                        #最大并发客户数
MOST_AUCTIONS=10                        #最大并发房间数
Function_dic={"login":1,"quit":2,
"auctions":3,"list":4,"join":5,"leave":6,"bid":7} #客户端功能对应编号
Bidder_dic={}                           #存储所有竞拍者的变量，eg:[冯小刚:bidder_a]表明：客户冯小刚已登录，bidder变量是bidder_a
Bidder_name_dic={}                      #存储竞拍者姓名，ID为键，姓名为值
Client_address_dic={}                   #地址池，eg：[1:Address_a]表明：id为1的用户的地址是Address_a（主机名,端口）
Auction_dic={}                          #存储所有竞拍室的变量，eg[name:auction_a]表明：auction_a房间的名字是name


class My_udp_handler(socketserver.BaseRequestHandler):      #与客户端交互的Handler
    def handle(self):
        data_list=self.request[0].decode('utf-8').split(' ')
        print("data_list=",data_list)
        function_id=Figure_Function(data_list)
        ret='0 无效命令！'
        if function_id==1:              #Login
            ret=Login(data_list,self.client_address)
        elif function_id==2:            #Quit
            ret=Quit(data_list)
        elif function_id==3:            #auctions输出所有竞拍室的情况
            ret=Show_all_auctions(data_list)
        elif function_id==4:            #list(auction)默认输出当前竞拍室的情况
            ret=Show_single_auction(data_list)
        elif function_id==5:            #Join(auction)
            ret=Join(data_list)
        elif function_id==6:            #Leave(auction)
            ret=Leave(data_list)
        elif function_id==7:            #Bid(price)
            ret=Bid(data_list)
        print("Auction_dic=",Auction_dic)
        print("bidder_dic=",Bidder_dic)
        print("Client_address_dic=",Client_address_dic)
        self.request[1].sendto(ret.encode('utf-8'),self.client_address)



Udp_server=socketserver.UDPServer(ADDRESS,My_udp_handler)   #服务器
Udp_server_socket=Udp_server.socket                         #取服务器的套接字


def Figure_Function(data_list)->int:    #确定客户端要调用的功能的序号，无效调用返回0
    try:
        if data_list[1].lower() in Function_dic:
            return Function_dic[data_list[1]]
    except:
        print('命令不明确')
        return 0

#----------------------------------------------------------------------------------------------------

def Login(data_list,cur_address):                   #客户端调用函数：用户登陆，编号1
    if len(data_list)!=3:
        return '0 Invalid command'
    if data_list[0]!='0':
        return '0 U have logged in'
    for i in range(1,MOST_BIDDERS+1):
        if(i not in Bidder_name_dic):
            _name=data_list[2]
            new_bidder=Bidder(i,_name)
            Bidder_dic[_name]=new_bidder
            Bidder_name_dic[i]=_name
            Client_address_dic[i]=cur_address       #记录ID:客户端地址对应关系
            return '1 '+str(i)+' '+_name
    return '0 Maximum concurrent'



def Quit(data_list):                    #客户端调用函数：用户退出（整个客户端退出，不是退出某一房间），编号2
    if len(data_list)!=2:
        return '0 Invalid command'
    _id=int(data_list[0])
    if _id<=0 or _id not in Bidder_name_dic:
        print('未登陆直接退出')
        return FINISH_FLAG
    if Leave(data_list)=='0 Leave failed, u are the Current highest bidder':#先离开当前竞拍室
        print(_id,'号用户未成功退出')
        return '0 你是当前出价最高者，不能退出'
    del Bidder_dic[Bidder_name_dic[_id]]
    del Bidder_name_dic[_id]
    del Client_address_dic[_id]
    print(_id,'号用户成功退出')
    return FINISH_FLAG


def Show_all_auctions(data_list):       #客户端调用函数：展示所有竞拍室的列表及参与者的情况，编号3
    if len(data_list)!=2:
        return '0 Invalid command'
    _id=int(data_list[0])
    if _id<=0 or _id not in Bidder_name_dic:
        return '0 U must login first'
    if not Auction_dic:
        return '1 There are no auctions right now'
    data='1 '
    for name in Auction_dic:
        data+='\n'+name+':\n'
        for i in Auction_dic[name].bidders:
            data+=Bidder_name_dic[i]+' '
    return data


def Show_single_auction(data_list):     #客户端调用函数：列出某竞拍室中参加竞拍的情况（所有竞拍者），编号4
    if len(data_list) not in(2,3):
        return '0 Invalid command'
    _id=int(data_list[0])
    if _id<=0 or _id not in Bidder_name_dic:
        return '0 U must login first'
    default_room=Bidder_dic[Bidder_name_dic[_id]].auction_name
    if len(data_list)==3:
        default_room=data_list[2]
    if default_room not in Auction_dic:
        return '0 Invalid auction name'
    data='1 '+default_room+':\n'
    for i in Auction_dic[default_room].bidders:
        data+=Bidder_name_dic[i]+' '
    return data


def Join(data_list):                    #客户端调用函数：加入某一竞拍室，服务器为其
#发送竞拍品目前的竞拍价格，及出价者。室中的所有竞拍者收到其加入的消息，编号5
    if len(data_list)!=3:
        return '0 Invalid command'
    _id=int(data_list[0])   #用户ID
    if _id<=0 or _id not in Bidder_name_dic:
        return '0 U must login first'
    _name=Bidder_name_dic[_id]#用户名
    _roomname=data_list[2]  #房间名
    if Bidder_dic[_name].auction_name:  #已经在另一房间，操作不允许
        return '0 你已在'+Bidder_dic[_name].auction_name+'房间，不允许再加入其它房间'
    if _roomname in Auction_dic:    #若要加入的房间存在
        #通知其房间内其他人
        msg=str(_id)+'号用户已加入当前房间'
        for i in Auction_dic[_roomname].bidders:
            i_address=Client_address_dic[i]
            Udp_server_socket.sendto(msg.encode('utf-8'),i_address)
        Bidder_dic[_name].auction_name=_roomname
        Auction_dic[_roomname].bidders.add(_id)
        return '1 成功加入房间\n当前出价：'+str(Auction_dic[_roomname].price)+'\n出价者：'+str(Auction_dic[_roomname].last_bidder_id)+'号竞拍者'
    else:                           #要加入的房间不存在
        return '0 未知房间名！'



def Leave(data_list):                   #客户端调用函数：离开某一竞拍室，编号6
    if len(data_list)!=2:
        return '0 Invalid command'
    _id=int(data_list[0])
    if _id<=0 or _id not in Bidder_name_dic:
        return '0 U must login first'
    _roomname=Bidder_dic[Bidder_name_dic[_id]].auction_name
    if not _roomname:
        return '0 U are not in any auction'
    if Auction_dic[_roomname].last_bidder_id==_id:
        return '0 Leave failed, u are the Current highest bidder'
    Bidder_dic[Bidder_name_dic[_id]].auction_name=''
    Auction_dic[_roomname].bidders.remove(_id)
    msg=str(_id)+'号用户已离开当前房间'
    for i in Auction_dic[_roomname].bidders:
        i_address=Client_address_dic[i]
        Udp_server_socket.sendto(msg.encode('utf-8'),i_address)
    return '1 Leave auction successfully'


def Bid(data_list):                     #客户端调用函数：为某一拍品出价，编号7
    if len(data_list)!=3:
        return '0 Invalid command'
    _id=int(data_list[0])
    if _id<=0 or _id not in Bidder_name_dic:
        return '0 U must login first'
    _price=0
    cur_auction=Bidder_dic[Bidder_name_dic[_id]].auction_name
    if not cur_auction:
        return '0 U are not in any auction, you can\'t bid'
    cur_auction=Auction_dic[cur_auction]
    try:    
        _price=int(data_list[2])
        if _price<=cur_auction.price:   #出的价不够高
            return '0 当前他人最高出价为：'+str(cur_auction.price)+'，请出更高的价格'
        cur_auction.price=_price
        cur_auction.cnt=0   #叫价次数归0，重新开始叫价
        cur_auction.last_bidder_id=_id
        msg=str(_id)+'号用户出价：'+str(_price)
        for i in cur_auction.bidders:   #告知同房间其他竞拍者
            if i!=_id:
                i_address=Client_address_dic[i]
                Udp_server_socket.sendto(msg.encode('utf-8'),i_address)
        return '1 成功出价：'+str(_price)
    except:
        return '0 Invalid command'
    



#上面是客户端调用的功能
#----------------------------------------------------------------------------------------------------
#下面是服务端管理员可使用的功能

Root_cur_auctionName=''                 #记录管理员当前在哪个竞拍室的全局变量

def OpenNewAuction(auction_name,price): #服务器自带功能：开通新的竞拍室
    global ui
    print('iiiiiiiiiiiiiiiiiiiii')
    if len(Auction_dic)==MOST_AUCTIONS:
        ui.textEdit.append('房间数已达最大，无法开通新房间')
        return
    if auction_name in Auction_dic:
        ui.textEdit.append('该房间名已被使用，无法注册房间')
        return
    new_auction=Auction(auction_name,price)
    Auction_dic[auction_name]=new_auction
    ui.textEdit.append('开通新房间:'+auction_name+'成功')



def Msg(msg,bidder_id=0):               #服务器自带功能：群发or向指定用户发送消息
    global ui
    if bidder_id==0:    #群发给所有人
        for i in Client_address_dic:
            Udp_server_socket.sendto(msg.encode('utf-8'),Client_address_dic[i])
    elif bidder_id>0:   #向指定用户发送
        if bidder_id in Bidder_name_dic:
            Udp_server_socket.sendto(msg.encode('utf-8'),Client_address_dic[bidder_id])
        else:
            ui.textEdit.append('Unauthorized client\'s ID')
    else:
        ui.textEdit.append('Invalid client\'s ID')


def Enter_auction(auction_name):        #服务器自带功能：进入并查看某一竞拍室的比赛情况
    global ui
    global Root_cur_auctionName
    if auction_name not in Auction_dic:
        ui.textEdit.append('Invalid auction name, please enter another valid auction')
        return
    ui.textEdit.append('成功进入'+auction_name)
    Root_cur_auctionName=auction_name


def List():                             #服务器自带功能：列出某竞拍室中参加竞拍者的情况
    global ui
    global Root_cur_auctionName
    if not Root_cur_auctionName:
        ui.textEdit.append('Haven\'t entered any auction')
        return
    if Root_cur_auctionName not in Auction_dic:
        ui.textEdit.append('Invalid auction name, please enter another valid auction')
        Root_cur_auctionName=''
        return
    auc=Auction_dic[Root_cur_auctionName]
    if not auc.bidders:
        ui.textEdit.append('当前竞拍室中还没有竞拍者加入')
        return
    try:
        ui.textEdit.append(Root_cur_auctionName+'中的竞拍者：')
        for _id in auc.bidders:
            ui.textEdit.append(str(_id)+'号用户 '+Bidder_name_dic[_id])
    except:
        ui.textEdit.append('Error!')

def List_all_auctions():                #服务器自带功能：列出当前正在竞拍行中正在进行的竞拍室
    global ui
    if not Auction_dic:
        ui.textEdit.append('No auctions exist now')
        return
    ui.textEdit.append('正在进行的所有竞拍室如下：')
    for auc in Auction_dic:
        ui.textEdit.append(auc)


def Leave_auction_cmd():                #服务器自带功能：管理员离开某一竞拍室
    global ui
    global Root_cur_auctionName
    if not Root_cur_auctionName:
        ui.textEdit.append('No need to leave any auction')
        return
    if Root_cur_auctionName not in Auction_dic:
        ui.textEdit.append('Invalid auction name, please enter another valid auction')
        Root_cur_auctionName=''
        return
    ui.textEdit.append('成功退出'+Root_cur_auctionName)
    Root_cur_auctionName=''


def Kickout(bidder_id):                 #服务器自带功能：踢人，并告知同竞拍室的其他人该消息
    global ui
    if bidder_id not in Bidder_name_dic:                #未登录的用户
        ui.textEdit.append('Unauthorized client\'s ID')
        return
    _roomname=Bidder_dic[Bidder_name_dic[bidder_id]].auction_name
    if not _roomname:                                   #不在任何房间
        ui.textEdit.append('This client hasn\'t entered any auction')
        return
    if Auction_dic[_roomname].last_bidder_id==bidder_id:#是最后出价者，踢人失败
        ui.textEdit.append('This client is the current highest bidder, kick failed!')
        return
    Udp_server_socket.sendto('你已经被管理员踢出该房间'.encode('utf-8'),Client_address_dic[bidder_id]) #通知客户端被踢出房间
    Auction_dic[_roomname].bidders.remove(bidder_id)                    #从当前竞拍室中踢出
    Bidder_dic[Bidder_name_dic[bidder_id]] .auction_name=''             #bidder_dic中调整相关记录
    msg=str(bidder_id)+'号用户已被管理员踢出该房间'
    for i in Auction_dic[_roomname].bidders:                            #通知同竞拍室的其他人
        if i!=bidder_id:
            Udp_server_socket.sendto(msg.encode('utf-8'),Client_address_dic[i])



def Close(_name):                       #服务器自带功能：关闭指定竞拍室，并告知其中每一位竞拍者
    global ui
    if _name not in Auction_dic:
        ui.textEdit.append('Invalid auction name')
        return
    msg='房间已被管理员关闭'
    for i in Auction_dic[_name].bidders:
        Udp_server_socket.sendto(msg.encode('utf-8'),Client_address_dic[i])
        Bidder_dic[Bidder_name_dic[i]].auction_name=''
    del Auction_dic[_name]
    ui.textEdit.append('Close auction successfully')

#----------------------------------------------------------------------------------------------------



def Terminal_input_handler(ui):           #处理服务器输入命令的函数
    # while True:
        # cmd=input('>>:').strip()
        cmd=ui.lineEdit.text()  #读命令输入框的命令
        ui.lineEdit.setText('') #清空输入框
        cmd_list=cmd.split(' ')
        print(cmd_list)
        x=cmd_list[0].lower()
        try:
            if x=='opennewauction' and len(cmd_list)==3:
                OpenNewAuction(cmd_list[1],int(cmd_list[2]))
            elif x=='enter' and len(cmd_list)==2:
                Enter_auction(cmd_list[1])
            elif x=='list':
                if len(cmd_list)>1:
                    ui.textEdit.append('Invalid command')
                List()
            elif x=='auctions' and len(cmd_list)==1:
                List_all_auctions() 
            elif x=='leave' and len(cmd_list)==1:
                Leave_auction_cmd()
            elif x=='msg':
                if len(cmd_list)==2:
                    Msg(cmd_list[1])
                elif len(cmd_list)>2:
                    try:
                        id=int(cmd_list[1])
                        if id>0 and id in Bidder_name_dic:
                            Msg(' '.join(cmd_list[2:]),id)
                        else:
                            Msg(' '.join(cmd_list[1:]))    
                    except:
                        Msg(' '.join(cmd_list[1:]))
                else:
                    ui.textEdit.append('You must input the message to be sent')
            elif x=='kickout' and len(cmd_list)==2:
                id=int(cmd_list[1])
                Kickout(id)
            elif x=='close' and len(cmd_list)==2:
                Close(cmd_list[1])
            else:
                ui.textEdit.append('Invalid command')
        except:
            ui.textEdit.append('Wrong command')

def Broadcast():
    while 1:
        time.sleep(10)
        need_deleted_auc=set()
        for auc in Auction_dic.values():
            if not auc.has_bidders():       #没人出价，就先不叫，有人出价了再叫价
                continue
            msg='第'+str(auc.cnt+1)+'次叫价，当前出价：'+str(auc.price)
            auc.cnt+=1
            for i in auc.bidders:
                i_address=Client_address_dic[i]
                Udp_server_socket.sendto(msg.encode('utf-8'),i_address)
            if auc.cnt==3:  #成交，发通知并善后处理
                need_deleted_auc.add(auc)   #加入待删除集合
        for auc in need_deleted_auc:
            msg=str(auc.last_bidder_id)+'号用户拍得该商品，您已退出到大厅'
            #给没拍到商品的人发通知
            for i in auc.bidders:
                if i!=auc.last_bidder_id:
                    i_address=Client_address_dic[i]
                    Udp_server_socket.sendto(msg.encode('utf-8'),i_address)
            msg='恭喜您拍得了该商品，您已退出到大厅'
            #给拍到商品的人发通知
            Udp_server_socket.sendto(msg.encode('utf-8'),Client_address_dic[auc.last_bidder_id])
            #关闭该房间
            #-----------------------------------------
            for i in auc.bidders:
                Bidder_dic[Bidder_name_dic[i]].auction_name=''  #退出该房间
            del Auction_dic[auc.auction_name]   #删除该房间
            #-----------------------------------------


def Server_init():
    Udp_server.serve_forever()              #服务器永远运行


# T_terminal_thread=threading.Thread(target=Terminal_input_handler,args=[])#线程2处理服务端的命令输入
# T_terminal_thread.setDaemon(True)
# T_terminal_thread.start()


T_terminal_thread=threading.Thread(target=Broadcast,args=[])#线程3处理所有竞拍室的实时广播价格和叫价
T_terminal_thread.setDaemon(True)
T_terminal_thread.start()


T_terminal_thread=threading.Thread(target=Server_init,args=[])#线程4处理UDP服务器的运行
T_terminal_thread.setDaemon(True)
T_terminal_thread.start()


app = QApplication(sys.argv)        #Ui界面是主线程，此线程退出则程序整体退出
Ui_Server = QMainWindow()
ui = Server_ui.Ui_Server()
ui.setupUi(Ui_Server)
ui.pushButton.clicked.connect(partial(Terminal_input_handler,ui))
Ui_Server.show()
sys.exit(app.exec_())