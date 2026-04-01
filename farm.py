import pyautogui 
import time 
import random 
import like_human
import click_dao
#Keo chuot den vi tri mo 
def drag_mouse(a,b,x,y): 
    #pyautogui.moveTo(x,y,duration=random.uniform(0.5,1)) 
    like_human.move_mouse_human(x,y)
    like_human.human_click()
    time.sleep(random.uniform(0.5,1)) 
    # Di chuyển chuột tới điểm bắt đầu 
    #pyautogui.moveTo(a + random.randint(-2, 2), b + random.randint(-2, 2), duration=random.uniform(0.25, 0.4)) 
    like_human.move_mouse_human(a,b)
    # Giữ chuột trái 
    pyautogui.mouseDown(button="left") 
    # Giữ một chút cho giống người 
    time.sleep(random.uniform(0.25, 0.35)) 
    # Kéo chuột tới điểm đích
    #pyautogui.moveTo(680, 418, random.uniform(0.25, 0.4)) 
    like_human.move_mouse_human(723,468)
    pyautogui.mouseUp(button="left")
    like_human.move_mouse_human(x,y)
