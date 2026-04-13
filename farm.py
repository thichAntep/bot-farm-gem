import pyautogui 
import time 
import random 
import like_human
import click_dao
from scan_is_mine import check_is_mine
#Keo chuot den vi tri mo 
def drag_mouse(a,b,x,y): 
    #x,y là tọa độ của đạo 
    like_human.move_mouse_human(x,y)
    like_human.human_click()
    time.sleep(random.uniform(0.5,1)) 
    like_human.move_mouse_human(a,b)
    # Giữ chuột trái 
    pyautogui.mouseDown(button="left") 
    # Giữ một chút cho giống người 
    time.sleep(random.uniform(0.25, 0.35)) 
    # Kéo chuột tới điểm đích
    #pyautogui.moveTo(680, 418, random.uniform(0.25, 0.4)) 
    mine_pos = check_is_mine()
    if mine_pos:
        x_mine, y_mine = mine_pos
        like_human.move_mouse_human(x_mine, y_mine)
    else:
        like_human.move_mouse_human(720,460)
    pyautogui.mouseUp(button="left")
    like_human.move_mouse_human(random.randint(500,500),random.randint(500,500))
