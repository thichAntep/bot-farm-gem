import like_human
import time
import random
from scan_star import scan_star
from scan_reset import scan_reset
from scan_farm_region import scan_region
import pyautogui
'''def farm_region(dao_index):
        time.sleep(random.uniform(0.5,1.5))
        star_pos = scan_star((0,0,500,200))
        x_star , y_star = star_pos
        if x_star is not None and y_star is not None:
            like_human.move_mouse_human(x_star , y_star)
            time.sleep(random.uniform(0.3223,0.533))
            pyautogui.click()
        
        x_db , y_db = scan_reset((450,200,170,200) )
        if x_db is not None and y_db is not None:
            like_human.move_mouse_human(x_db , y_db)
            time.sleep(random.uniform(0.3223,0.533))
            like_human.click_mouse()
        x_region , y_region = scan_region((550,328+dao_index*70,550,50))
        if x_region is not None and y_region is not None:
            like_human.move_mouse_human(x_region , y_region)
            time.sleep(random.uniform(0.3223,0.533))
            like_human.click_mouse()
        '''
def farm_region(dao_index):
    time.sleep(random.uniform(0.5,1.5))

    # STAR
    star_pos = scan_star((100, 30, 300, 200))
    if star_pos:
        x_star, y_star = star_pos
        like_human.move_mouse_human(x_star , y_star)
        time.sleep(random.uniform(0.3223,0.533))
        pyautogui.click()
    else:
        print("Không thấy star")

    # RESET
    time.sleep(random.uniform(0.5,1))
    reset_pos = scan_reset((450,200,170,200))
    if reset_pos:
        x_db, y_db = reset_pos
        like_human.move_mouse_human(x_db , y_db)
        time.sleep(random.uniform(0.3223,0.533))
        like_human.human_click()
    else:
        like_human.human_click(1065,251)

    # REGION
    time.sleep(random.uniform(0.5,1))
    region_pos = scan_region((550,328+(dao_index-1)*66,550,50))
    if region_pos:
        x_region, y_region = region_pos
        like_human.move_mouse_human(x_region , y_region)
        time.sleep(random.uniform(0.3223,0.533))
        like_human.human_click()
        time.sleep(random.uniform(0.5,1))
    else:
        like_human.human_click(1065,251)