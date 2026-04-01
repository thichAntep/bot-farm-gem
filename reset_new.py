import like_human
import pyautogui
import time
import scan_icon_hanh_quan
import random
import move_map
import scan_reset

def click_if_hanh_quan(max_wait=8.0):
    directions = ["left", "right", "up", "down"]

    # Né mỏ tranh ban đầu
    for _ in range(3):
        direction = random.choice(directions)
        print(f"↪ Né mỏ tranh: {direction}")
        move_map.move_one_step(direction, move_time=0.5)
        time.sleep(random.uniform(0.4, 0.7))

    # Căn lại map
    move_map.move_one_step("down", move_time=0.5)

    print("🔎 Bắt đầu vòng lặp quét hành quân...")
    start_time = time.time()
    while time.time() - start_time < max_wait:
        pos = scan_icon_hanh_quan.scan_hanh_quan()

        if pos:
            x_o, y_o = pos
            x = x_o + random.randint(175,185)
            y = y_o + random.randint(95,105)
           
            print(f"✅ Phát hiện hành quân tại ({x}, {y})")

            like_human.move_mouse_human(x, y)
            time.sleep(0.4)
            pyautogui.click()

            like_human.human_click(
                random.randint(1167, 1270),
                random.randint(281, 310)
            )
            time.sleep(random.uniform(0.5, 0.8))
            pos_reset = scan_reset.scan_reset((800, 550, 463, 307))

            if pos_reset:
                x_reset, y_reset = pos_reset

                like_human.move_mouse_human(
                    x_reset + random.randint(-2, 2),
                    y_reset + random.randint(-2, 2)
                )
                pyautogui.click()

            else:
                print("⚠ Không tìm thấy nút reset")
                return False

            like_human.move_mouse_human(
                random.randint(770, 920),
                random.randint(666, 683)
            )
            pyautogui.click()

            return True  # ✅ xong việc → thoát

        # ❌ KHÔNG CÓ ICON → giả hành vi người
        print("❌ Chưa thấy hành quân → fake hành vi")

        like_human.move_mouse_human(
            random.randint(300, 1000),
            random.randint(200, 640)
        )
        pyautogui.click()

        time.sleep(random.uniform(0.5, 0.8))

    print("⏰ Hết thời gian chờ hành quân")
    return False