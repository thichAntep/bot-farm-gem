# move_map.py
import time
import random
import keyboard

def spiral_step_generator():
    """
    Generator sinh từng bước xoắn ốc (KHÔNG loop nội bộ)
    Trả về: 'left' | 'right' | 'up' | 'down'
    """
    step = 1
    while True:
        for _ in range(step):
            yield "right"
        for _ in range(step):
            yield "down"
        step += 1

        for _ in range(step):
            yield "left"
        for _ in range(step):
            yield "up"
        step += 1


def move_one_step(direction,move_time):
    keyboard.press(direction)
    time.sleep(random.uniform(move_time-0.15, move_time+0.15))
    keyboard.release(direction)
    time.sleep(random.uniform(1, 1.2))
 # Ví dụ gọi hàm di chuyển một bước sang phải