import cv2
import numpy as np
import pyautogui
import time
import mss

from resource_path import resource_path

# =============================
# CONFIG
# =============================

TEMPLATE_LIST = [
    "images/bug1.png", #lienminh
    "images/bug2.png", #hienatai
    "images/bug3.png", #hientai
    "images/bug4.png",#hientai
    "images/bug5.png",#tuido
]

THRESHOLD = 0.6
SCAN_TIME_PER_REGION = 2.0   # mỗi vùng quét tối đa 2s
SLEEP_BETWEEN_SCAN = 0.3

SCAN_REGIONS = [
    (202,133,1000,600),
    (5, 60, 100, 100),
    (600, 510, 250, 80),
    (202,133,1000,600),
    (202,133,1000,600),
    (1050,190,60,60)
]
BUG_INFO = [
    {
        "name": "lienminh",
        "template": "images/bug1.png",
        "region": (202,133,1000,600)
    },
    {
        "name": "hienatai",
        "template": "images/bug2.png",
        "region": (10, 10, 300, 300)
    },
    {
        "name": "hientai",
        "template": "images/bug3.png",
        "region": (600, 510, 250, 80)
    },
    {
        "name": "hientai_2",
        "template": "images/bug4.png",
        "region": (202,133,1000,600)
    },
    {
        "name": "tuido",
        "template": "images/bug5.png",
        "region": (202,133,1000,600)
    },
        {
        "name": "hientai_4",
        "template": "images/bug6.png",
        "region": (1050,190,60,60)
    },
    

]

# =============================
# UTILS
# =============================

def safe_region(region):
    screen_w, screen_h = pyautogui.size()
    x, y, w, h = region

    if x < 0 or y < 0:
        return None
    if w <= 0 or h <= 0:
        return None
    if x + w > screen_w or y + h > screen_h:
        return None

    return x, y, w, h


def load_templates():
    templates = []
    for path in TEMPLATE_LIST:
        img = cv2.imread(resource_path(path))
        if img is None:
            print(f"❌ Không load được {path}")
            continue
        templates.append(img)
    return templates


TEMPLATES = load_templates()

# =============================
# MAIN SCAN FUNCTION
# =============================
def load_bug_info():
    bugs = []
    for bug in BUG_INFO:
        img = cv2.imread(resource_path(bug["template"]))
        if img is None:
            print(f"❌ Không load được {bug['template']}")
            continue

        bug["img"] = img
        bugs.append(bug)

    return bugs


BUGS = load_bug_info()

def scan_bug_multi_region():
    """
    Trả về:
    {
        'bug': tên bug,
        'pos': (x, y),
        'score': match score
    }
    """

    if not BUGS:
        print("❌ Không có bug để scan")
        return None

    for idx, bug in enumerate(BUGS, start=1):
        region = safe_region(bug["region"])
        if region is None:
            continue

        template = bug["img"]
        bug_name = bug["name"]

        x0, y0, w0, h0 = region
        start_time = time.time()

        print(f"🔍 Scan BUG {idx} | {bug_name}")

        while time.time() - start_time < SCAN_TIME_PER_REGION:
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
                break

            sh, sw = screen.shape[:2]
            th, tw = template.shape[:2]

            if sh < th or sw < tw:
                time.sleep(SLEEP_BETWEEN_SCAN)
                continue

            result = cv2.matchTemplate(
                screen,
                template,
                cv2.TM_CCOEFF_NORMED
            )

            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            if max_val >= THRESHOLD:
                x, y = max_loc
                real_x = x0 + x + tw // 2
                real_y = y0 + y + th // 2

                print(
                    f"\n🐞 BUG FOUND: {bug_name} "
                    f"| score={max_val:.2f} "
                    f"| pos=({real_x},{real_y})"
                )

                return {
                    "bug": bug_name,
                    "pos": (int(real_x), int(real_y)),
                    "score": float(max_val)
                }

            time.sleep(SLEEP_BETWEEN_SCAN)

    return None




# =============================
# TEST
# =============================
if __name__ == "__main__":
    pos = scan_bug_multi_region()
    print("KẾT QUẢ:", pos)
