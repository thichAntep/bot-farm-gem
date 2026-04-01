import pyautogui
import random
import time
import math

# =========================
# HÀM PHỤ
# =========================

def clamp(v, min_v, max_v):
    return max(min_v, min(v, max_v))


def bezier_curve(p0, p1, p2, p3, t):
    """Bezier cubic"""
    return (
        (1 - t)**3 * p0 +
        3 * (1 - t)**2 * t * p1 +
        3 * (1 - t) * t**2 * p2 +
        t**3 * p3
    )


# =========================
# DI CHUYỂN GIỐNG NGƯỜI
# =========================

def move_mouse_human(
    x, y,
    min_time=0.25,
    max_time=0.6,
    steps_range=(25, 45),
    offset=8
):

    start_x, start_y = pyautogui.position()

    screen_w, screen_h = pyautogui.size()

    end_x = x + random.randint(-offset, offset)
    end_y = y + random.randint(-offset, offset)

    # tránh góc màn hình
    end_x = clamp(end_x, 5, screen_w - 5)
    end_y = clamp(end_y, 5, screen_h - 5)

    cp1_x = start_x + random.randint(-100, 100)
    cp1_y = start_y + random.randint(-100, 100)

    cp2_x = end_x + random.randint(-100, 100)
    cp2_y = end_y + random.randint(-100, 100)

    steps = random.randint(*steps_range)
    total_time = random.uniform(min_time, max_time)
    sleep_time = total_time / steps

    for i in range(steps + 1):

        t = i / steps
        t = math.sin(t * math.pi / 2)

        x_pos = bezier_curve(start_x, cp1_x, cp2_x, end_x, t)
        y_pos = bezier_curve(start_y, cp1_y, cp2_y, end_y, t)

        # clamp lại lần nữa
        x_pos = clamp(int(x_pos), 5, screen_w - 5)
        y_pos = clamp(int(y_pos), 5, screen_h - 5)

        pyautogui.moveTo(x_pos, y_pos, _pause=False)

        time.sleep(sleep_time * random.uniform(0.8, 1.2))

def human_click(x=None, y=None):
    if x is not None and y is not None:
        move_mouse_human(x, y)

    time.sleep(random.uniform(0.05, 0.15))
    pyautogui.mouseDown()
    time.sleep(random.uniform(0.06, 0.12))
    pyautogui.mouseUp()


# =========================
# DRAG GIỐNG NGƯỜI
# =========================

def human_drag(start_x, start_y, end_x, end_y):
    move_mouse_human(start_x, start_y)
    time.sleep(random.uniform(0.05, 0.15))

    pyautogui.mouseDown()
    time.sleep(random.uniform(0.08, 0.15))

    move_mouse_human(
        end_x, end_y,
        min_time=0.3,
        max_time=0.7,
        steps_range=(30, 55),
        offset=6
    )

    time.sleep(random.uniform(0.05, 0.12))
    pyautogui.mouseUp()
