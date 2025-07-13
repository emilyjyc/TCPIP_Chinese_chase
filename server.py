from tkinter import *
import socket               # 導入 socket 模組
import asyncio
import time
import sys
import threading
import json, types,string
from struct import *
from ctypes import *
from collections import namedtuple

Color = namedtuple('RGB','red, green, blue')
colors = {} #dict of colors
class RGB(Color):
    def hex_format(self):
        return '#{:02X}{:02X}{:02X}'.format(self.red,self.green,self.blue)

BURLYWOOD = RGB(222, 184, 135)
BURLYWOOD4 = RGB(139, 115, 85)
DARKSALMON = RGB(233, 150, 122)
LIGHTSALMON4 = RGB(139, 87, 66)

colors['burlywood'] = BURLYWOOD
colors['burlywood4'] = BURLYWOOD4
colors['darksalmon'] = DARKSALMON
colors['lightsalmon4'] = LIGHTSALMON4

g_qipan = [None]*50
g_count = 0


def circle(canvas, x, y, r, color=None):
    id = canvas.create_oval(x-r, y-r, x+r, y+r, fill = color)
    return id


class 	Cpixel:
    def __init__(self, m, n):
        self.x = m
        self.y = n

class Cpoint:
    def __init__(self, m, n):
        self.x = m
        self.y = n


class Cqizi:
    def __init__(self, point = None, color = 'burlywood', str = "", alive = 1):
        self.point = point
        self.str = str
        self.color = color
        self.focus = 0
        self.focus_color = 'darksalmon'
        self.last_color = "gray"
        self.alive = alive
    def set_point(self, point):
        self.point = point
    def set_focus(self):
        self.focus = 1
    def clear_focus(self):
        self.focus = 0
    def dead(self):
        self.alive = 0
    def is_alive(self):
        return self.alive

    #start為棋盤開始的像素點， gap為棋盤相鄰交叉點距離
    def paint(self, master, start, gap):
        r = gap*3/8
        circle(master, start.x + self.point.x * gap, start.y + self.point.y * gap, r, self.color)
        if self.focus == 1:
            circle(master, start.x + self.point.x * gap, start.y + self.point.y * gap, gap*9/16, self.focus_color)
        master.create_text(start.x + self.point.x * gap, start.y + self.point.y * gap, text=self.str)



class Cqipan:
    #start_piexl為棋盤開始的像素點， gap為棋盤相鄰交叉點距離
    def __init__(self, start_piexl, gap, master, sock, color):
        self.m_over = 0
        self.m_master = master
        self.m_current_player = 'burlywood'
        self.m_choose_qizi = None
        self.m_start_piexl = start_piexl
        self.m_gap = gap
        self.sock = sock
        self.m_color = color
        self.m_yline_count = 9
        self.m_xline_count = 10
        self.qizilist = []
        self.pointlist = []
#生成所有棋子，並初始化其座標
        x = 0
        y = 0
        redcolor='burlywood'

        self.qizilist.append(Cqizi(Cpoint(x,y), redcolor,  "車"))
        x += 1
        self.qizilist.append(Cqizi(Cpoint(x,y), redcolor,  "馬"))
        x += 1
        self.qizilist.append(Cqizi(Cpoint(x,y), redcolor,  "象"))
        x += 1
        self.qizilist.append(Cqizi(Cpoint(x,y), redcolor,  "士"))
        x += 1
        self.qizilist.append(Cqizi(Cpoint(x,y), redcolor,  "帥"))
        x += 1
        self.qizilist.append(Cqizi(Cpoint(x,y), redcolor,  "士"))
        x += 1
        self.qizilist.append(Cqizi(Cpoint(x,y), redcolor,  "象"))
        x += 1
        self.qizilist.append(Cqizi(Cpoint(x,y), redcolor,  "馬"))
        x += 1
        self.qizilist.append(Cqizi(Cpoint(x,y), redcolor,  "車"))

        x = 0
        y = 3
        self.qizilist.append(Cqizi(Cpoint(x,y), redcolor,  "兵"))
        x += 2
        self.qizilist.append(Cqizi(Cpoint(x, y), redcolor, "兵"))
        x += 2
        self.qizilist.append(Cqizi(Cpoint(x, y), redcolor, "兵"))
        x += 2
        self.qizilist.append(Cqizi(Cpoint(x, y), redcolor, "兵"))
        x += 2
        self.qizilist.append(Cqizi(Cpoint(x, y), redcolor, "兵"))

        x = 1
        y = 2
        self.qizilist.append(Cqizi(Cpoint(x, y), redcolor, "炮"))
        x += 6
        self.qizilist.append(Cqizi(Cpoint(x, y), redcolor, "炮"))


        x = 0
        y = self.m_xline_count - 1
        greencolor = 'burlywood4'

        self.qizilist.append(Cqizi(Cpoint(x,y), greencolor,  "車"))
        x += 1
        self.qizilist.append(Cqizi(Cpoint(x,y), greencolor,  "馬"))
        x += 1
        self.qizilist.append(Cqizi(Cpoint(x,y), greencolor,  "象"))
        x += 1
        self.qizilist.append(Cqizi(Cpoint(x,y), greencolor,  "士"))
        x += 1
        self.qizilist.append(Cqizi(Cpoint(x,y), greencolor,  "將"))
        x += 1
        self.qizilist.append(Cqizi(Cpoint(x,y), greencolor,  "士"))
        x += 1
        self.qizilist.append(Cqizi(Cpoint(x,y), greencolor,  "象"))
        x += 1
        self.qizilist.append(Cqizi(Cpoint(x,y), greencolor,  "馬"))
        x += 1
        self.qizilist.append(Cqizi(Cpoint(x,y), greencolor,  "車"))

        x = 0
        y = 6
        self.qizilist.append(Cqizi(Cpoint(x,y), greencolor,  "卒"))
        x += 2
        self.qizilist.append(Cqizi(Cpoint(x, y), greencolor, "卒"))
        x += 2
        self.qizilist.append(Cqizi(Cpoint(x, y), greencolor, "卒"))
        x += 2
        self.qizilist.append(Cqizi(Cpoint(x, y), greencolor, "卒"))
        x += 2
        self.qizilist.append(Cqizi(Cpoint(x, y), greencolor, "卒"))

        x = 1
        y = 7
        self.qizilist.append(Cqizi(Cpoint(x, y), greencolor, "炮"))
        x += 6
        self.qizilist.append(Cqizi(Cpoint(x, y), greencolor, "炮"))

    # 生成所有有效點
        x = 0
        y = 0
        for i in range(self.m_yline_count):
            for j in range(self.m_xline_count):
                self.pointlist.append(Cpoint(x+i, y+j))


    #像素點到棋盤交點轉换 pixel_start為棋盤開始的像素點， pixel為要轉換的像素點， gap為棋盤相鄰兩個交叉點距離
    def pixel_to_point(self, pixel):

        gap = self.m_gap
        x = self.m_start_piexl.x + gap * (self.m_yline_count-1)
        y = self.m_start_piexl.y + gap * (self.m_xline_count-1)
        end_piexl = Cpixel(x, y)

        r = gap*3/8

        if (pixel.x < (self.m_start_piexl.x - r) or pixel.x > (end_piexl.x + r) or pixel.y < (self.m_start_piexl.y - r) or pixel.y > (end_piexl.y + r)):
            return None

        pixel.x = pixel.x - self.m_start_piexl.x
        pixel.y = pixel.y - self.m_start_piexl.y

        for item in self.pointlist:
            if pixel.x <= (item.x*gap + r) and pixel.x >= (item.x*gap - r) and pixel.y <= (item.y*gap + r) and pixel.y > (item.y*gap - r):
                return item
        return None


    #判斷兩點是否在一條直線上
    def on_same_line(self, point1, point2):
        if (point1.x == point2.x and point1.y != point2.y) or (point1.y == point2.y and point1.x != point2.x):
            return 1
        else:
            return 0
    #棋子列表，查看是否有棋子位於兩點之間的線上
    def no_qizi_on_line(self, point1, point2):
        if self.on_same_line(point1, point2) == 0:
            return 0
        for item in self.qizilist:
            #如果是Y方向直線
            if item.is_alive() and item.point.x == point1.x and item.point.x == point2.x and item.point.y != point1.y and item.point.y != point2.y:
                if (item.point.y > point1.y and item.point.y > point2.y) or (item.point.y < point1.y and item.point.y < point2.y):
                    continue
                else:
                    return 0
            #如果是X方向直線
            if item.is_alive() and item.point.y == point1.y and item.point.y == point2.y and item.point.x != point1.x and item.point.x != point2.x:
                if (item.point.x > point1.x and item.point.x > point2.x) or (item.point.x < point1.x and item.point.x < point2.x):
                    continue
                else:
                    return 0
        return 1
    #判斷兩點是否為日子形
    def on_rizi_line(self, point1, point2):
        # X坐標差1，y坐標差2
        if (abs(point1.x - point2.x) == 1 and abs(point1.y-point2.y) == 2):
            return 1
        # X坐標差2，y坐標差1
        if (abs(point1.x - point2.x) == 2 and abs(point1.y - point2.y) == 1):
            return 1
        return 0;
    
    def no_qizi_on_rizi(self, point1, point2):
        if self.on_rizi_line(point1, point2) == 0:
            return 0
        #馬可以走8個方向，每個方向對應一個別子坐標
        dic = {(1,-2):Cpoint(point1.x, point1.y-1),
               (2,-1):Cpoint(point1.x+1, point1.y),
               (2,1): Cpoint(point1.x + 1, point1.y),
               (1,2): Cpoint(point1.x, point1.y+1),
               (-1,2):Cpoint(point1.x, point1.y+1),
               (-2,1):Cpoint(point1.x - 1, point1.y),
               (-2,-1):Cpoint(point1.x - 1, point1.y),
               (-1,-2):Cpoint(point1.x, point1.y-1)
               }
        x_difference = point2.x - point1.x
        y_difference = point2.y - point1.y
        key = (x_difference, y_difference)
        bie_point =  dic[key]
        for item in self.qizilist:
            #如果是Y方向直線
            if item.point.x == bie_point.x and item.point.y == bie_point.y:
                print("get bie point")
                return 0
        print("no bie point")
        return 1

    #判斷兩點是否為田字形
    def on_tianzi_line(self, point1, point2):
        # X坐標差2，y坐標差
        if (abs(point1.x - point2.x) == 2 and abs(point1.y-point2.y) == 2):
            return 1

        return 0;
    #遍歷棋子列表，查看是否有棋子位於田字路徑上
    def no_qizi_on_tianzi(self, point1, point2):
        if self.on_tianzi_line(point1, point2) == 0:
            return 0
        #馬可以走4個方向，每個個方向對應一個別子坐標
        dic = {(2,2):Cpoint(point1.x+1, point1.y+1),
               (-2,2):Cpoint(point1.x-1, point1.y+1),
               (2,-2): Cpoint(point1.x + 1, point1.y-1),
               (-2,-2): Cpoint(point1.x-1, point1.y-1)
               }
        x_difference = point2.x - point1.x
        y_difference = point2.y - point1.y
        key = (x_difference, y_difference)
        bie_point =  dic[key]
        for item in self.qizilist:
            #如果是Y方向直線
            if item.point.x == bie_point.x and item.point.y == bie_point.y:
                print("get bie point")
                return 0
        print("no bie point")
        return 1


    # 判斷兩點是否為口字形 且point2 必須不能出宮
    def on_kouzi_line(self, point1, point2):

        if self.m_current_player == 'burlywood':
            if point2.x < 3 or point2.x > 5 or point2.y < 0 or point2.y > 2:
                return 0
        if self.m_current_player == 'burlywood4':
            if point2.x < 3 or point2.x > 5 or point2.y > 9 or point2.y < 7:
                return 0
        # X坐標差1，y坐標差1
        if (abs(point1.x - point2.x) == 1 and abs(point1.y - point2.y) == 1):
            return 1

        return 0

    # 判斷兩點是否為一字形 且point2必須不能出宮
    def on_yizi_line(self, point1, point2):

        if self.m_current_player == 'burlywood':
            if point2.x < 3 or point2.x > 5 or point2.y < 0 or point2.y > 2:
                return 0
        if self.m_current_player == 'burlywood4':
            if point2.x < 3 or point2.x > 5 or point2.y > 9 or point2.y < 7:
                return 0
        # X坐標差1，y坐標差1
        if (abs(point1.x - point2.x) == 1 and point1.y == point2.y) or (point1.x == point2.x and abs(point1.y - point2.y) == 1):
            return 1

        return 0

    # 判斷兩點是否為一字形 且point2只能向前
    def on_bingzi_line(self, point1, point2):
        if self.m_current_player == 'burlywood':
            if point2.y < point1.y or (point1.y < 5 and point1.x != point2.x):
                return 0
        if self.m_current_player == 'burlywood4':
            if point2.y > point1.y or (point1.y >=  5 and point1.x != point2.x):
                return 0
        # X坐標差1，y坐標差1
        if (abs(point1.x - point2.x) == 1 and point1.y == point2.y) or (point1.x == point2.x and abs(point1.y - point2.y) == 1):
            return 1

    def one_qizi_on_line(self, point1, point2):
        qizi_count = 0
        if self.on_same_line(point1, point2) == 0:
            return 0
        for item in self.qizilist:
            # 如果是Y方向直線
            if item.is_alive() and item.point.x == point1.x and item.point.x == point2.x and item.point.y != point1.y and item.point.y != point2.y:
                if (item.point.y > point1.y and item.point.y > point2.y) or (
                        item.point.y < point1.y and item.point.y < point2.y):
                    continue
                else:
                    qizi_count = qizi_count+1
            # 如果是X方向直線
            if item.is_alive() and item.point.y == point1.y and item.point.y == point2.y and item.point.x != point1.x and item.point.x != point2.x:
                if (item.point.x > point1.x and item.point.x > point2.x) or (
                        item.point.x < point1.x and item.point.x < point2.x):
                    continue
                else:
                    qizi_count = qizi_count + 1
        if qizi_count == 1:
            return 1

        return 0

    def qizi_on_point(self, point):
        for item in self.qizilist:
            if item.is_alive():
                if item.point.x == point.x and item.point.y == point.y:
                    return item
        return None

    def go(self, qizi, point):
        #point是否位於棋盤線交叉點，是則返回交叉點，否則返回NONE
        focus_point = point
        if focus_point == None:
            return 0

        if qizi.str == "車":
            #車走直線，所以判斷兩點是否在同一條直線
            if self.on_same_line(qizi.point, focus_point):
                #車行走的路徑中不能有其他棋子
                if self.no_qizi_on_line(qizi.point, focus_point):
                    chizi = self.qizi_on_point(focus_point)
                    if chizi != None:
                        if qizi.color != chizi.color:
                            chizi.dead()
                        else:
                            return 0
                    qizi.set_point(focus_point)
                    return 1
            return 0

        if qizi.str == "馬":
            #馬走日子，且不能有别的馬棋子
            if self.on_rizi_line(qizi.point, focus_point):
                #馬走日字且不能有别棋子
                if self.no_qizi_on_rizi(qizi.point, focus_point):
                    chizi = self.qizi_on_point(focus_point)
                    if chizi != None:
                        if qizi.color != chizi.color:
                            chizi.dead()
                        else:
                            return 0
                    qizi.set_point(focus_point)
                    return 1

        if qizi.str == "象":
            #象走田字，且路徑上不能有其它棋子
            if self.on_tianzi_line(qizi.point, focus_point):
                if self.no_qizi_on_tianzi(qizi.point, focus_point):
                    chizi = self.qizi_on_point(focus_point)
                    if chizi != None:
                        if qizi.color != chizi.color:
                            chizi.dead()
                        else:
                            return 0
                    qizi.set_point(focus_point)
                    return 1
        if qizi.str == "士":
            #士走口字
            if self.on_kouzi_line(qizi.point, focus_point):
                chizi = self.qizi_on_point(focus_point)
                if chizi != None:
                    if qizi.color != chizi.color:
                        chizi.dead()
                    else:
                        return 0
                qizi.set_point(focus_point)
                return 1

        if qizi.str == "將" or qizi.str == "帥":
            #將走一字
            if self.on_yizi_line(qizi.point, focus_point):
                chizi = self.qizi_on_point(focus_point)
                if chizi != None:
                    if qizi.color != chizi.color:
                        chizi.dead()
                    else:
                        return 0
                qizi.set_point(focus_point)
                return 1

        if qizi.str == "兵" or qizi.str == "卒":
            #兵走一字 只向前
            if self.on_bingzi_line(qizi.point, focus_point):
                chizi = self.qizi_on_point(focus_point)
                if chizi != None:
                    if qizi.color != chizi.color:
                        chizi.dead()
                    else:
                        return 0
                qizi.set_point(focus_point)
                return 1

        if qizi.str == "炮":
            #炮走直線，所以判斷兩點是否在同一條直線,且路徑上必須只能有一個棋子
            if self.on_same_line(qizi.point, focus_point):
                #車行走的路徑中不能有其他棋子
                chizi = self.qizi_on_point(focus_point)
                if chizi != None:
                    if self.one_qizi_on_line(qizi.point, focus_point):
                        if qizi.color != chizi.color:
                            chizi.dead()
                            qizi.set_point(focus_point)
                            return 1
                else:
                    if self.no_qizi_on_line(qizi.point, focus_point):
                        qizi.set_point(focus_point)
                        return 1
            return 0

        return 0

    def check_win(self):
        red = 0;
        green = 0;
        for item in self.qizilist:
            if item.str == "帥" and item.is_alive():
                red = 1
            if item.str == "將" and item.is_alive():
                green = 1
        if red == 0:
            self.m_master.create_text(self.m_start_piexl.x + self.m_gap*4, self.m_start_piexl.y + self.m_gap*10, text="绿方赢")
            self.m_over = 1
        if green == 0:
            self.m_master.create_text(self.m_start_piexl.x + self.m_gap * 4, self.m_start_piexl.y + self.m_gap * 10, text="红方赢")
            self.m_over = 1


    def paint(self):
        start = self.m_start_piexl
        gap = self.m_gap

        self.m_master.delete('all')
        for i in range(self.m_xline_count):
            self.m_master.create_line(start.x, (start.y + i*gap), (start.x + (self.m_yline_count-1)*gap), (start.y + i*gap), fill="#476042")

        for i in range(self.m_yline_count):
            self.m_master.create_line((start.x + i*gap), start.y, (start.x + i*gap), (start.y + (self.m_xline_count-1)*gap), fill="#476042")

        for item in self.qizilist:
            if item.is_alive():
                item.paint(self.m_master, start, gap)

    def send_qizi_info(self):
        test_count = 0
        for item in self.qizilist:
            msg = [{'name':item.str, 'color':item.color, 'x':item.point.x, 'y':item.point.y, 'focus':item.focus, 'alive':item.alive}]
            jmsg = json.dumps(msg)
            jmsg_len  = len(jmsg)
            pack_msg = pack("l", jmsg_len)
            self.sock.send(pack_msg)
            self.sock.send(bytes(jmsg, 'utf-8'))
            print("send:", item.str, " x:", item.point.x, " y:", item.point.y)


    def get_point(self, event, piexl = 0, witch = 'burlywood'):
        if self.m_over == 1  or self.m_current_player != witch:
            return None
        x, y = event.x, event.y
        if piexl == 0:
            #獲取點對應的棋盤交叉點
            focus_point = self.pixel_to_point(Cpixel(x, y))
        else:
            focus_point = Cpoint(x, y)

        if focus_point != None:
            #查看改點是否落在棋子上
            qizi = self.qizi_on_point(focus_point)
            #如果還沒有選定棋子
            if self.m_choose_qizi == None:
                if qizi != None and qizi.color == self.m_current_player:
                    self.m_choose_qizi = qizi
                    self.m_choose_qizi.set_focus()
                    self.paint()
            #如果已經選定過棋子
            else:
                #本次新點擊的棋子也屬於己方，則切換選定點到新棋子上
                if qizi != None and qizi.color == self.m_current_player:
                    self.m_choose_qizi.clear_focus()
                    self.m_choose_qizi = qizi
                    self.m_choose_qizi.set_focus()
                    self.paint()
                #移動
                else:
                    ret = self.go(self.m_choose_qizi, focus_point)
                    if ret == 1:
                        self.m_choose_qizi.clear_focus()
                        self.m_choose_qizi = None
                        self.paint()
                        self.player_switch()
        self.check_win()
        self.send_qizi_info()
        print(x, y)

    def player_switch(self):
        if self.m_current_player == 'burlywood':
            self.m_current_player = 'burlywood4'
        else:
            self.m_current_player = 'burlywood'


def net_rec(i, sock):
    while True:
        data = sock.recv(2)
        print(len(data))
        if not data:
            continue
        g_qipan[i].get_point(Cpoint(data[0], data[1]), piexl = 1, witch = 'green')


def task_func(c, addr, i):
    global g_qipan

    print('in task_func')
    print('連接地址：', addr)
    c.send(bytes('歡迎連接！', encoding='utf-8'))

    frame = Tk()
    canvas_width = 800
    canvas_height = 600
    master = Canvas(frame,
                      width=canvas_width,
                      height=canvas_height)

    master.pack()

    start_pixel = Cpixel(150, 30)
    g_qipan[i] = Cqipan(start_pixel, 50, master, c, 'burlywood')

    g_qipan[i].paint()

    master.bind("<Button-1>", g_qipan[i].get_point)

    thread = threading.Thread(target=net_rec, args=(i, c, ))
    thread.start()

    frame.mainloop()

    return 'the result'


s = socket.socket()  # 創建 socket 對象
host = '192.168.187.224'  # 獲取本地主機名
port = 5555  # 設置埠號
s.bind((host, port))  # 绑定埠號


s.listen(5)  # 等待客户端連接

print("waitting for connection...")
while True:
    c, addr = s.accept()  # 建立客户端連接。
	
    thread = threading.Thread(target=task_func, args=(c, addr,g_count, ))
    thread.start()
    g_count += 1













