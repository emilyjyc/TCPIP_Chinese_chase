import pygame
from pygame.locals import *
import sys
import time
import traceback
import chess_pieces
from constant import Constant
import random

# 初始化
pygame.init()
try:
    pygame.mixer.init()
except:
    print("您沒有音樂設備！")
    raise Exception

bg_size = width, height = Constant.chess_bg_width, Constant.chess_bg_height
screen = pygame.display.set_mode(bg_size)
bg_rect = screen.get_rect()
pygame.display.set_caption("象棋小遊戲")

# 初始化音樂
pygame.mixer.music.load('../sounds/bg.ogg')

# 初始化圖片

chess_pan_img = pygame.image.load('../image/chess_bg.png').convert()
chess_select1_img = pygame.image.load('../image/black_select.png').convert_alpha()
chess_select2_img = pygame.image.load('../image/red_select.png').convert_alpha()

# 初始化移動，翻棋子，吃棋子
choosed = False

# 初始化字體
my_font = pygame.font.Font('../font/simhei.ttf', Constant.font_size)

# 定義顏色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# 象棋 1*將 + 2*（士+象+馬+車+炮）+ 5*兵 = 一共16子*2 = 32子
chess_class = []  # [shi_chess,xiang_chess,ma_chess,che_chess,pao_chess]*2
for j in range(2):
    for i in range(2):
        chess_class.append(chess_pieces.ShiChess(bg_rect))
        chess_class.append(chess_pieces.XiangChess(bg_rect))
        chess_class.append(chess_pieces.MaChess(bg_rect))
        chess_class.append(chess_pieces.CheChess(bg_rect))
        chess_class.append(chess_pieces.PaoChess(bg_rect))

    chess_class.append(chess_pieces.JiangChess(bg_rect))
    for i in range(5):
        chess_class.append(chess_pieces.ZuChess(bg_rect))

# 一半的棋子為黑色
for i in range(len(chess_class) // 2):
    chess_class[i].role = chess_pieces.BLACK_ROLE

running = True

# 首先翻牌的為type:0
player_role = chess_pieces.BLACK_ROLE


def getChessList():
    # 產生隨機數 0-31
    resultList = random.sample(range(0, 32), 32);
    j = 0;
    # print('chess_class 的長度 %d  resultList 的長度 %d' % (len(chess_class),len(resultList)))
    for i in resultList:
        # print((i,j,chess_class[j].type))
        chess_class[j].position = (Constant.padding_left + (i % 4) * Constant.box_width, \
                                   Constant.padding_top+ ((i // 4)) * Constant.box_height)
        chess_class[j].rect.left = Constant.padding_left + (i % 4) * Constant.box_width
        chess_class[j].rect.top = Constant.padding_top + ((i // 4)) * Constant.box_height
        # print(chess_class[j].position)
        j += 1
    return chess_class


def is_chess_clicked(chess_list, event):
    for each in chess_list:
        if (each.rect.collidepoint(event.pos)):
            return each
    return None


def operation_completed():
    global player_role
    if player_role == chess_pieces.BLACK_ROLE:
        player_role = chess_pieces.RED_ROLE
    else:
        player_role = chess_pieces.BLACK_ROLE


def draw_text(text, font_color, center):
    mytext = my_font.render(text, True, font_color)
    text_rect = mytext.get_rect()
    text_rect.center = center
    screen.blit(mytext, text_rect)


def main():
    global player_role
    overturn_count = 0
    # 初始化音樂
    pygame.mixer.music.play(-1)
    clock = pygame.time.Clock()
    # 被打亂後，且有位置信息的對象數組
    chess_list = getChessList()
    selected_img_rect = chess_select1_img.get_rect()
    selected_img_rect.left = -100
    selected_img_rect.top = -100
    select_chess = None
    # is_start = False

    player1_role = chess_pieces.BLACK_ROLE
    player2_role = chess_pieces.BLACK_ROLE

    player1_color = BLACK
    player2_color = BLACK
    global running

    while running:

        # 首先繪製棋盤
        screen.blit(chess_pan_img, (10, 10))

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # 按下滑鼠左鍵 ###
                    # print(event.pos)
                    selected = is_chess_clicked(chess_list, event)
                    # print(selected)
                    if selected is not None:
                        # 本次點擊有點擊到棋子
                        if selected.state == chess_pieces.CHOOSED_STATE:
                            pass
                        elif selected.state == chess_pieces.ACTIVE_STATE:
                            if player_role == selected.role:
                                # 當前玩家點擊到自己的棋子
                                select_chess = selected
                                selected.state = chess_pieces.ACTIVE_STATE
                                selected_img_rect.left = selected.rect.left
                                selected_img_rect.top = selected.rect.top
                            else:
                                # 當前玩家點擊到别的玩家的棋子
                                if select_chess is not None:
                                    # 判斷是否可以吃該棋子
                                    if select_chess.eat(selected, event.pos, chess_list):
                                        operation_completed()
                                        select_chess = None

                        elif selected.state == chess_pieces.HIDDEN_STATE:
                            # 翻轉
                            selected.state = chess_pieces.ACTIVE_STATE
                            selected_img_rect.left = selected.rect.left
                            selected_img_rect.top = selected.rect.top
                            # is_start = True  暫時認為該標籤沒有用
                            if overturn_count == 0:
                                player_role = selected.role
                            # 統計翻轉的次數
                            overturn_count += 1
                            # 如果當前翻出的是對方的棋子，則為對方自動選擇該棋子
                            if selected.role is not player_role:
                                select_chess = selected
                            else:
                                select_chess = None
                            # 翻轉之後相當於一次操作完成
                            operation_completed()
                    else:
                        # 本次點擊没有點擊棋子，只是點擊到了棋盤
                        print('本次點擊只點擊到棋盤，請再點擊一次')
                        print(select_chess)

                        if select_chess is not None:
                            # 判斷被選中的棋子是否可以移動到當前位置
                            if select_chess.move(event.pos):
                                operation_completed()
                                select_chess = None

        # 繪製棋子
        for each in chess_list:
            # pass
            if each.state is not chess_pieces.DEAD_STATE:
                screen.blit(each.getImage(each.role), each.rect)
            # print(each.position)
        # 繪製被選中的圖標
        # print(player_role)
        if player_role == chess_pieces.BLACK_ROLE:
            screen.blit(chess_select1_img, selected_img_rect)
        else:
            screen.blit(chess_select2_img, selected_img_rect)

        # 繪製當前玩家提示
        marked_words = ''
        font_color = RED
        if overturn_count == 1:
            player1_role = player_role
            if player1_role == chess_pieces.BLACK_ROLE:
                player1_color = BLACK
            else:
                player1_color = RED

        if overturn_count == 2:
            player2_role = player_role
            if player2_role == chess_pieces.BLACK_ROLE:
                player2_color = BLACK
            else:
                player2_color = RED

        if player_role == player1_role:
            marked_words = '玩家1'
            font_color = player1_color
        else:
            marked_words = '玩家2'
            font_color = player2_color
        # 確定顏色
        if overturn_count == 0:
            marked_words = '未選定顏色，請玩家1翻牌'
            font_color = GREEN

        draw_text(marked_words, font_color, (width // 2, Constant.font_size))

        # 判斷遊戲是否结束
        # 方法，計算棋盤上存活的棋子數量，如果為零就，停止
        black_count = 0
        red_count = 0
        for each in chess_list:
            if each.state == chess_pieces.ACTIVE_STATE or each.state == chess_pieces.HIDDEN_STATE:
                if each.role == chess_pieces.BLACK_ROLE:
                    black_count += 1
                else:
                    red_count += 1

        if black_count == 0:
            # 紅方勝利
            draw_text('紅方勝利 !', RED, (width // 2, height // 2))
        elif red_count == 0:
            # 黑方勝利
            draw_text('黑方勝利 !', BLACK, (width // 2, height // 2))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        print("遊戲正常退出")
    except:
        print("遊戲退出異常")
        traceback.print_exc()
        pygame.quit()
        input()
