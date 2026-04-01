import pyautogui
import time
import random
import like_human
import math
#CHon doi quan
def click_mouse(a,b):
    time.sleep(0.3)
    #Di chuot den dao ranh
    like_human.move_mouse_human(a,b)
    pyautogui.mouseDown(button="left") 
    time.sleep(random.uniform(0.15, 0.2))
    pyautogui.mouseUp(button="left")
    time.sleep(random.uniform(0.25, 0.3))


    #Mo rong Map
    like_human.move_mouse_human(random.randint(395,1110),random.randint(180,600))
    time.sleep(random.uniform(0.25, 0.3))
    for _ in range(random.randint(3,3)):
        pyautogui.mouseDown(button = "left")
        pyautogui.scroll(-1)
    pyautogui.mouseUp(button = "left")
    time.sleep(random.uniform(1,2))
def thu_nho_map():
    like_human.move_mouse_human(random.randint(395,1110),random.randint(180,600))
    time.sleep(random.uniform(0.25, 0.3))
    like_human.human_click()
    time.sleep(random.uniform(0.2, 0.6))
def mo_rong_map():
    like_human.move_mouse_human(random.randint(395,1110),random.randint(180,600))
    time.sleep(random.uniform(0.25, 0.3))
    for _ in range(random.randint(3,3)):
        pyautogui.mouseDown(button = "left")
        pyautogui.scroll(-1)
        time.sleep(random.uniform(0.2, 0.6))
    pyautogui.mouseUp(button = "left")


