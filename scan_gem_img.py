import cv2
import numpy as np
import mss
import math
from resource_path import resource_path
def scan_gem():
    # ================= KHỞI TẠO 1 LẦN DUY NHẤT =================
    if not hasattr(scan_gem, "is_initialized"):
        # Xóa dòng scan_gem.sct = mss.mss() vì mss không an toàn khi truyền qua lại giữa các thread
        
        # 1. Danh sách 7 regions
        scan_gem.regions = [
            (5, 50, 500, 390),
            (0, 350, 600, 300),
            (460, 50, 520, 300),
            (560, 300, 450, 370),
            (520, 610, 500, 210),
            (950, 50, 320, 350),
            (950, 400, 350, 300)
        ]
        
        # 2. KHAI BÁO TÊN ẢNH
        image_files_per_region = [
            ["images/gem_vung_11.png", "images/gem_vung_12.png"], 
            ["images/gem_vung_21.png", "images/gem_vung_22.png"],                       
            ["images/gem_vung_31.png",  "images/gem_vung_32.png"],                       
            ["images/gem_vung_41.png",  "images/gem_vung_42.png"],                       
            ["images/gem_vung_51.png",  "images/gem_vung_52.png"],                       
            ["images/gem_vung_61.png",  "images/gem_vung_62.png"],                       
            ["images/gem_vung_71.png",  "images/gem_vung_72.png"]                        
        ]
        
        # 3. Load toàn bộ ảnh vào RAM
        scan_gem.templates = []
        for file_list in image_files_per_region:
            region_templates = []
            for file_name in file_list:
                full_path = resource_path(file_name)
                img = cv2.imread(full_path, 0)
                if img is not None:
                    region_templates.append({"name": file_name, "img": img})
                else:
                    print(f"[Cảnh báo] Không tìm thấy file ảnh: {full_path}")
            scan_gem.templates.append(region_templates)
            
        scan_gem.is_initialized = True

    # ================= BẮT ĐẦU QUÉT =================
    # 1. Chụp toàn màn hình
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screen = np.array(sct.grab(monitor))
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGRA2GRAY)
    
    # Tính tọa độ trung tâm của màn hình
    screen_center_x = monitor["left"] + monitor["width"] // 2
    screen_center_y = monitor["top"] + monitor["height"] // 2
    
    closest_center = None
    min_distance = float('inf') # Khởi tạo khoảng cách nhỏ nhất là vô cực
    
    # 2. Duyệt qua 7 vùng
    for i, region in enumerate(scan_gem.regions):
        x, y, w, h = region
        region_templates = scan_gem.templates[i]
        
        if not region_templates:
            continue
            
        region_img = screen_gray[y:y+h, x:x+w]
        
        # 3. Quét các ảnh
        for template in region_templates:
            temp_img = template["img"]
            th, tw = temp_img.shape
            
            if th > h or tw > w:
                continue
                
            res = cv2.matchTemplate(region_img, temp_img, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            
            if max_val >= 0.85: 
                center_x = x + max_loc[0] + (tw // 2)
                center_y = y + max_loc[1] + (th // 2)
                
                # Tính khoảng cách bình phương từ gem này tới trung tâm màn hình (dùng bình phương cho nhẹ máy, ko cần sqrt)
                distance = (center_x - screen_center_x)**2 + (center_y - screen_center_y)**2
                
                # Cập nhật nếu tìm thấy gem gần trung tâm hơn
                if distance < min_distance:
                    min_distance = distance
                    closest_center = (center_x, center_y)
                
    # Chỉ trả về duy nhất 1 tọa độ (hoặc None nếu không thấy)
    return closest_center

        