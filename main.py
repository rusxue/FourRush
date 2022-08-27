import os
import sys
import threading
from configparser import ConfigParser
from socket import *

import numpy as np
import pygame


# 渲染区
# 渲染棋盘棋子
def Render_zsz():
    screen.blit(qipan, (0, 0))
    for x in range(4):
        for y in range(4):
            if qipan_mat[x, y] == 0:
                pass
            elif qipan_mat[x, y] == 1:
                screen.blit(white, (160 + 140 * y, 10 + 140 * x))
            else:
                screen.blit(black, (160 + 140 * y, 10 + 140 * x))


# 渲染选中框
def Render_so(before_p):
    if move:
        screen.blit(selected, (160 + 140 * before_p[1], 10 + 140 * before_p[0]))
    else:
        for x in range(4):
            for y in range(4):
                if qipan_mat[x, y] == 0:
                    pass
                elif qipan_mat[x, y] == 1 and types == 1:
                    screen.blit(optional, (160 + 140 * y, 10 + 140 * x))
                elif qipan_mat[x, y] == 2 and types == 2:
                    screen.blit(optional, (160 + 140 * y, 10 + 140 * x))


# 格式化点击操作
def get_mouseqipan(event):
    mouse_x, mouse_y = event.pos
    if (
        490 > mouse_y > 10
        and 640 > mouse_x > 160
        and (mouse_y - 10) % 140 <= 60
        and (mouse_x - 160) % 140 <= 60
    ):
        mouse_y, mouse_x = (mouse_y - 10) // 140, (mouse_x - 160) // 140
        return True, (mouse_y, mouse_x)
    else:
        return False, 0


# 选定将要移动的棋子（移动第一步）
def move_click_before(p_bfore, qipan_mat, type):
    if qipan_mat[p_bfore[0], p_bfore[1]] == type:
        return True, p_bfore
    else:
        return False, 0


# 选择将要移向的空位（移动第二步）
def move_click_back(p_back, qipan_mat, P_before):
    if (
        qipan_mat[p_back[0], p_back[1]] == 0
        and (p_back[0] == P_before[0] or p_back[1] == P_before[1])
        and (
            p_back[0] + p_back[1] + 1 == P_before[0] + P_before[1]
            or p[0] + p[1] == P_before[0] + P_before[1] + 1
        )
    ):
        return True, p_back
    else:
        return False, 0


# 逻辑区
# 初始化棋盘
def ini_scene():
    global qipan_mat
    if liuzichong:
        qipan_mat = np.mat("1,1,1,1;1,0,0,1;2,0,0,2;2,2,2,2")
    else:
        qipan_mat = np.mat("1,1,1,1;1,0,0,0;0,0,0,0;2,2,2,2")


# 判断场上棋子总数，确定胜负状态
def win_zsz(qipan_mat):
    alive1 = qipan_mat[qipan_mat == 1].size
    alive2 = qipan_mat[qipan_mat == 2].size
    if 0 < alive1 < 2:
        return 2
    elif 0 < alive2 < 2:
        return 1
    else:
        return 0


# 杀死棋子
def kill_zsz(qipan_mat, place, x, bool):
    if bool:
        qipan_mat[place[0], x] = 0
    else:
        qipan_mat[x, place[1]] = 0
    return qipan_mat


# 移动
def move_zsz(qipan_mat, o_place, n_place):
    if qipan_mat[n_place[0], n_place[1]] == 0:
        a = qipan_mat[o_place[0], o_place[1]]
        qipan_mat[n_place[0], n_place[1]] = a
        qipan_mat[o_place[0], o_place[1]] = 0
    else:
        pass
    return qipan_mat


# 存活判断
def alive_zsz(qipan_mat, place):
    type = qipan_mat[place[0], place[1]]
    h = 1
    for i in [qipan_mat[place[0], :], qipan_mat[:, place[1]].T]:
        if i.sum() == type + 3 and (i[0, 0] == 0 or i[0, 3] == 0):
            if i[0, 0] != i[0, 2] and i[0, 0] != 0:
                if type == i[0, 0]:
                    kill_zsz(qipan_mat, place, 2, h)
                else:
                    kill_zsz(qipan_mat, place, 0, h)
            elif i[0, 1] != i[0, 3] and i[0, 3] != 0:
                if type == i[0, 3]:
                    kill_zsz(qipan_mat, place, 1, h)
                else:
                    kill_zsz(qipan_mat, place, 3, h)
            else:
                pass
        else:
            pass
        h = 0
    else:
        pass
    return qipan_mat


# 改变棋盘上下方向
def change_zsz(qipan_mat):
    c = np.mat("0,0,0,0;0,0,0,0;0,0,0,0;0,0,0,0")
    for i in range(4):
        c[i, :] = qipan_mat[3 - i, :]
    return c


# 交互


def tcp_interact():
    global messages
    global game_live
    while game_live:
        qipan_str = client_socket.recv(1024)
        messages = np.fromstring(qipan_str, dtype=int).reshape(4, 4)


qipan_mat = np.mat("1,1,1,1;0,0,0,0;0,0,0,0;2,2,2,2")  # 初始化变量
mainpath = os.getcwd()
clock = pygame.time.Clock()  # 设置时钟

# 初始化数据
game_live = 1
recv_data = ""
move = 0
p_before = (0, 0)
win_able = 0
messages = np.mat("")
message_o = np.mat("")

liuzichong = 0
types = 2  # 先后手（1后2先）
interactable = 0  # 交互开关
inter_mode = 0  # 默认ai
tcp_type = 1  # tcp主机开关
port = 9999
ip = "127.0.0.1"

if os.path.exists(mainpath + "\config.ini"):  # 读取配置文件
    configini = ConfigParser()
    configini.read("config.ini", encoding="utf-8")
    liuzichong = configini.getint("main", "liuzichong")
    types = configini.getint("main", "type")
    interactable = configini.getint("interract", "interactable")
    inter_mode = configini.getint("interract", "inter_mode")
    tcp_type = configini.getint("tcp", "tcp_type")
    port = configini.getint("tcp", "port")
    ip = configini.get("tcp", "ip")

tp1 = types
pygame.init()  # 初始化pygame
size = width, height = 800, 500  # 设置窗口大小
screen = pygame.display.set_mode(size)  # 显示窗口
color = (0, 0, 0)  # 设置颜色
pygame.display.set_caption("走石子")
ini_scene()

qipan = pygame.image.load(mainpath + r"\screen.png")  # 加载图片资源
white = pygame.image.load(mainpath + r"\white.png")
black = pygame.image.load(mainpath + r"\black.png")
optional = pygame.image.load(mainpath + r"\optional.png")
selected = pygame.image.load(mainpath + r"\selected.png")
gg = pygame.image.load(mainpath + r"\gg.png")
winpng = pygame.image.load(mainpath + r"\win.png")
losepng = pygame.image.load(mainpath + r"\lose.png")

if interactable and not inter_mode:  # 尝试tcp连接
    if tcp_type:
        tcp_server_socket = socket(AF_INET, SOCK_STREAM)
        address = ("127.0.0.1", port)
        tcp_server_socket.bind(address)
        tcp_server_socket.listen(128)
        client_socket, clientAddr = tcp_server_socket.accept()
        recv_data = client_socket.recv(1024).decode("gbk")  # 接收1024个字节
        if recv_data == "1":
            client_socket.send("1".encode("gbk"))
          

    else:
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((ip, port))
        client_socket.send("1".encode("gbk"))
        recvData = client_socket.recv(1024).decode("gbk")
        if recvData == "1":
            pass

if interactable and not inter_mode:  # 创建监听端口线程减轻无响应问题
    thread = threading.Thread(target=tcp_interact)
    thread.start()

while True:  # 主程序
    clock.tick(10)  # 每秒执行10次
    for event in pygame.event.get():  # 遍历所有事件
        if event.type == pygame.QUIT:  # 如果单击关闭窗口，则退出
            if interactable and not inter_mode:
                game_live = 0
            sys.exit()

        if types == 0:
            pass
        elif interactable and types == 1:  # 交互性开启,接受数据

            if (
                win_able and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            ):  # 胜利画面后重开游戏
                x_p, y_p = event.pos
                if 570 > x_p > 330 and 350 > y_p > 300:
                    ini_scene()
                    types = tp1
                    move = 0
                    win_able = 0

            if inter_mode:
                pass
            elif message_o != messages:
                message_mat = np.mat(messages)
                for abnx in range(4):
                    qipan_mat[abnx, :] = message_mat[3 - abnx, :]
                    for nm in range(4):
                        if qipan_mat[abnx, nm] == 1:
                            qipan_mat[abnx, nm] = 2
                        elif qipan_mat[abnx, nm] == 2:
                            qipan_mat[abnx, nm] = 1
                message_o = messages
                if types == 1:
                    types = 2
                else:
                    types = 1

            if win_zsz(qipan_mat) != 0:
                win_able = 1
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if win_able:  # 胜利画面后重开游戏
                x_p, y_p = event.pos
                if 570 > x_p > 330 and 350 > y_p > 300:
                    ini_scene()
                    types = tp1
                    move = 0
                    win_able = 0

            if get_mouseqipan(event)[0]:  # 棋子移动
                p = get_mouseqipan(event)[1]
                if not move:  # 第一步
                    if move_click_before(p, qipan_mat, types)[0]:
                        p_before = move_click_before(p, qipan_mat, types)[1]
                        move = 1
                else:  # 第二步
                    if move_click_back(p, qipan_mat, p_before)[0]:
                        p_back = move_click_back(p, qipan_mat, p_before)[1]
                        move = 0

                        # 结算移动
                        if types == 1:
                            types = 2
                        else:
                            types = 1
                        move_zsz(qipan_mat, p_before, p_back)
                        alive_zsz(qipan_mat, p_back)
                        if win_zsz(qipan_mat) != 0:
                            win_able = 1
                        if interactable:
                            client_socket.send(qipan_mat.tobytes())
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # 右键取消选定
            move = 0

    screen.fill(color) 
    Render_zsz()
    Render_so(p_before)
    if win_able:
        screen.blit(gg, (0, 0))
        if win_zsz(qipan_mat) == 2:
            screen.blit(winpng, (0, 0))
        elif win_zsz(qipan_mat) == 1:
            screen.blit(losepng, (0, 0))

    pygame.display.flip()  # 更新全部显示

# pygame.quit()
