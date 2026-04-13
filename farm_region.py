import like_human
import time
import random
from scan_star import scan_star
from scan_reset import scan_reset
from scan_farm_region import scan_region
import pyautogui
from scan_find_images import scan_find

# Lưu trữ tọa độ farm của tối đa 7 đạo
dao_farm_coords = {}

def set_farm_coordinates(coords_dict):
    """
    Nhận dictionary chứa tọa độ farm từ GUI 
    { 1: (x, y), 2: (x, y), ... }
    """
    global dao_farm_coords
    dao_farm_coords.clear()
    dao_farm_coords.update(coords_dict)

def setup_farm_coordinates(num_daos):
    """
    Hàm này được gọi trước khi bot chạy nếu tích chọn farm.
    Cho phép người dùng nhập tọa độ farm cho từng đạo (tối đa 7).
    """
    global dao_farm_coords
    dao_farm_coords.clear()
    
    # Giới hạn tối đa 7 đạo
    num_daos = min(num_daos, 7)
    
    print(f"\n--- YÊU CẦU NHẬP TỌA ĐỘ FARM CHO {num_daos} ĐẠO ---")
    for i in range(1, num_daos + 1):
        while True:
            try:
                coord_input = input(f"Nhập tọa độ cho đạo {i} (định dạng X,Y ví dụ: 500,600): ")
                parts = coord_input.split(',')
                if len(parts) != 2:
                    raise ValueError("Phải nhập cả X và Y phân tách bằng dấu phẩy.")
                
                x = int(parts[0].strip())
                y = int(parts[1].strip())
                dao_farm_coords[i] = (x, y)
                print(f"-> Đã lưu tọa độ ({x}, {y}) cho đạo {i}")
                break
            except ValueError as e:
                print(f"Lỗi nhập liệu: Xin vui lòng nhập đúng định dạng số X,Y.")

def farm_region(dao_index):
    # Phần này kiểm tra và click vào phần tìm kiếm ảnh
    star_pos = scan_star((100, 30, 300, 200))
    if star_pos:
        x_star, y_star = star_pos
        like_human.move_mouse_human(x_star - random.randint(40, 60), y_star+random.randint(0, 3))
        time.sleep(random.uniform(0.3223,0.533))
        pyautogui.click()
    else:
        return
    find_pos = scan_find((500,150,500,300))
    if find_pos:
        x_find, y_find = find_pos
    else:
        return
    like_human.move_mouse_human(x_find + random.randint(-200,-190), y_find + random.randint(-2,2))
    time.sleep(random.uniform(0.2,0.35))
    pyautogui.click()
    time.sleep(random.uniform(0.5,1))
    #Nhạp tọa độ X cho vùng farm
    coord = dao_farm_coords.get(dao_index)
    if coord:
        print(f"Đạo {dao_index} đang dùng tọa độ farm đã lưu: X={coord[0]}, Y={coord[1]}")
        # Gõ phím tọa độ X của đạo index đã lưu
        time.sleep(random.uniform(0.2, 0.5))
        pyautogui.write(str(coord[0]), interval=random.uniform(0.05, 0.15))

    time.sleep(random.uniform(0.5,1.5))
    like_human.move_mouse_human(x_find+random.randint(-90,-80),y_find+random.randint(-3,3))
    time.sleep(random.uniform(0.2,0.35))
    pyautogui.click()
    time.sleep(random.uniform(0.5,1))
    #Nhập tọa độ Y cho vùng farm
    coord = dao_farm_coords.get(dao_index)
    if coord:
        print(f"Đạo {dao_index} đang dùng tọa độ farm đã lưu: Y={coord[1]}")
        # Gõ phím tọa độ Y của đạo index đã lưu
        time.sleep(random.uniform(0.2, 0.5))
        pyautogui.write(str(coord[1]), interval=random.uniform(0.05, 0.15))
    time.sleep(random.uniform(0.5,1.5))
    #Di chuyen den vung farm sau khi Nhap 
    like_human.move_mouse_human(x_find+random.randint(-3,3),y_find+random.randint(-3,3))
    pyautogui.click()
    time.sleep(random.uniform(0.5,1))

    
