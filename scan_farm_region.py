# scan_return_img.py
import cv2
import numpy as np
import mss
import pyautogui
from resource_path import resource_path

TEMPLATE_PATH = "images/region.png"
THRESHOLD = 0.65
def safe_region(region):
    """
    Đảm bảo vùng quét không vượt màn hình
    """
    screen_w, screen_h = pyautogui.size()
    x, y, w, h = region

    if x < 0 or y < 0:
        return None
    if w <= 0 or h <= 0:
        return None
    if x + w > screen_w or y + h > screen_h:
        return None

    return x, y, w, h


def scan_region(scan_region):
    """
    scan_region: (x, y, w, h)
    return: (x, y) tọa độ màn hình hoặc None
    """

    # 1️⃣ kiểm tra region
    scan_region = safe_region(scan_region)
    if scan_region is None:
        print("❌ scan_region không hợp lệ")
        return None

    x0, y0, w0, h0 = scan_region

    # 2️⃣ load template
    template = cv2.imread(resource_path(TEMPLATE_PATH))
    if template is None:
        print("❌ Không load được quay_ve.png")
        return None

    th, tw = template.shape[:2]

    # 3️⃣ chụp màn hình bằng MSS (KHÔNG CRASH THREAD)
    try:
        with mss.mss() as sct:
            monitor = {
                "left": x0,
                "top": y0,
                "width": w0,
                "height": h0
            }
            screenshot = sct.grab(monitor)
            screen = np.array(screenshot)
            screen = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
    except Exception as e:
        print("❌ MSS grab failed:", e)
        return None

    # 4️⃣ match template
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    ys, xs = np.where(result >= THRESHOLD)

    if len(xs) == 0:
        return None

    # 5️⃣ lấy kết quả đầu tiên
    x, y = xs[0], ys[0]

    # 6️⃣ quy đổi về tọa độ màn hình thật (tâm ảnh)
    real_x = x0 + x + tw // 2
    real_y = y0 + y + th // 2

    return int(real_x), int(real_y)
