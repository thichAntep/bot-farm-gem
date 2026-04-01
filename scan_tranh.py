import cv2
import numpy as np
import pyautogui
from resource_path import resource_path   # ✅ THÊM DÒNG NÀY

# ảnh nằm trong thư mục images/
TEMPLATE_LIST = [
    "images/tranh1.png",
    "images/tranh2.png",
    "images/tranh3.png",
    "images/tranh4.png"
]

THRESHOLD = 0.65
SCAN_REGION = (650,350,200,200)  # x, y, w, h


def find_one_image():
    # 1️⃣ chụp màn hình 1 lần
    screenshot = pyautogui.screenshot(region=SCAN_REGION)
    screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # 2️⃣ duyệt từng template
    for template_path in TEMPLATE_LIST:
        full_path = resource_path(template_path)  # ✅ FIX ĐƯỜNG DẪN

        template = cv2.imread(full_path)
        if template is None:
            print(f"❌ Không load được ảnh: {template_path}")
            continue

        h, w = template.shape[:2]

        # 3️⃣ match
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        ys, xs = np.where(result >= THRESHOLD)

        if len(xs) > 0:
            x, y = xs[0], ys[0]

            x = SCAN_REGION[0] + x + w // 2
            y = SCAN_REGION[1] + y + h // 2

            print(f"✅ Found {template_path} at ({x},{y})")
            return int(x), int(y)

    return None
