class Bidder:       #竞拍者类
    bidder_id=0     #系统分配的id
    auction_name=''    #所处的竞拍室房间名
    address=(0,0)       #客户端地址(IP,端口)
    def __init__(self,_id=0,_name=''):
        self.bidder_id=_id
        self.bidder_name=_name      #姓名
    def is_logined(self):
        return self.bidder_id!=0
    def print(self):
        print('id=',self.bidder_id,'name=',self.bidder_name,'auction_name=',self.auction_name,'address=',self.address)