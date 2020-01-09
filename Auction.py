import time
import threading
class Auction:      #竞拍室类
    price=0     #起拍价
    cnt=0       #叫了几次价了
    def __init__(self,_name='',_price=0):
        self.auction_name=_name     #竞拍室名字
        self.price=_price
        self.bidders=set()      #当前竞拍室中的所有竞拍者集合
        self.last_bidder_id=0   #最后出价的竞拍者编号
    def has_bidders(self):
        return self.last_bidder_id!=0
