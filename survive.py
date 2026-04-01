import cv2
import numpy as np
import pyautogui

from resource_path import resource_path

# =============================
# CONFIG
# =============================

TEMPLATE_LIST = [
    "images/survive1.png",
    "images/survive2.png",
    "images/survive3.png",
    "images/survive4.png",
    "images/survive5.png",
]

SCAN_REGIONS = [
    (1365, 200, 65, 60),
    (1365, 260, 65, 60),
    (1365, 320, 65, 60),
    (1365, 380, 65, 60),
    (1365, 440, 65, 60),
    (1365, 500, 65, 60),
    (1365, 560, 65, 60),
]

THRESHOLD = 0.50


# =============================
# LOAD TEMPLATE
# =============================

TEMPLATES = []
for p in TEMPLATE_LIST:
    img = cv2.imread(resource_path(p), cv2.IMREAD_GRAYSCALE)
    if img is None:
        print("❌ Load fail:", p)
    else:
        TEMPLATES.append(img)

print("✅ Template loaded:", len(TEMPLATES))


# =============================
# SCAN
# =============================

def count_survive_icon():
    count = 0

    for idx, (x, y, w, h) in enumerate(SCAN_REGIONS, start=1):
        # chụp đúng ô
        screen = pyautogui.screenshot(region=(x, y, w, h))
        screen = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2GRAY)

        found = False
        best = 0.0

        for tpl in TEMPLATES:
            res = cv2.matchTemplate(screen, tpl, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            best = max(best, max_val)

            if max_val >= THRESHOLD:
                found = True
                break

        if found:
            count += 1
            print(f"✅ Ô {idx} MATCH | score={best:.2f}")
        else:
            print(f"❌ Ô {idx} NO MATCH | best={best:.2f}")

    return count


# =============================
# TEST
# =============================

if __name__ == "__main__":
    total = count_survive_icon()
    print(f"\n🎯 TOTAL ICON = {total}/{len(SCAN_REGIONS)}")
