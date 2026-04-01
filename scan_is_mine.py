import pyautogui
import cv2
import numpy as np
import os
from resource_path import resource_path

CONF = 0.7

# list ảnh template
MINE_TEMPLATES = [
    "images/mo1.png",
    "images/mo2.png"  # Xóa khoảng trắng bị dư ở cuối
]

def check_is_mine():
    screenshot = pyautogui.screenshot(region=(450, 320, 500, 250))
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    for img_path in MINE_TEMPLATES:
        # 1. Chuyển đổi đường dẫn tương đối thành đường dẫn tuyệt đối trong file exe
        absolute_path = resource_path(img_path)
        
        # 2. Đọc ảnh bằng đường dẫn tuyệt đối vừa tạo
        template = cv2.imread(absolute_path)

        if template is None:
            # In ra đường dẫn tuyệt đối để dễ debug nếu thiếu file
            print("❌ Không đọc được ảnh tại:", absolute_path)
            continue

        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)

        print(f"🔍 Check {img_path} → {round(max_val,2)}")

        if max_val >= CONF:
            print("⛏ Đây là mỏ (match:", img_path, ")")
            return True

    print("❌ Không phải mỏ")
    return False