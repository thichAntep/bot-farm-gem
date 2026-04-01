import threading
import time
import tkinter as tk
from tkinter import ttk
import keyboard
import pyautogui
import random
import ctypes
import sys
import queue
import ctypes
# ===== IMPORT BOT MODULE =====
import like_human
from scan_gem_img import scan_gem
from scan_return_img import scan_return
from scan_stop_img import scan_stop
from reset_new import click_if_hanh_quan
from farm import drag_mouse
from click_dao import click_mouse, thu_nho_map, mo_rong_map
from choose_dao import random_point_in_dao
import move_map
import scan_tranh
from scan_bug import scan_bug_multi_region
import survive
ctypes.windll.shell32.ShellExecuteW(None, "runas", "python", __file__, None, 1)
# Tránh máy tính sleep
ctypes.windll.kernel32.SetThreadExecutionState(
    0x80000002  # ES_CONTINUOUS | ES_SYSTEM_REQUIRED
)

# =============================
# CONFIG VÙNG QUÉT ĐẠO
# =============================
DAO_START_REGION = (1365, 200, 65, 60)  # đạo 1
DAO_OFFSET_Y = 60                       # mỗi đạo lệch 60px
MAX_DAO = 7
HANH_QUAN_INTERVAL = 5 * 60             # 5 phút
LAST_HANH_QUAN_SCAN = 0
MISS_LIMIT = 1                          # thiếu liên tiếp bao nhiêu lần mới reset
_last_miss_count = 0                    # bộ nhớ thiếu đạo

# =============================
# STATE BOT & CONFIG KHÁC
# =============================
BOT_RUNNING = False
BOT_PAUSE = False
BUG_SCAN_INTERVAL = 3 * 60              # 3 phút
LAST_BUG_SCAN_TIME = 0

RANDOM_CLICK_INTERVAL = 2 * 60          # 2 phút
RANDOM_CLICK_PROB = 0.80                # 80%
LAST_RANDOM_CLICK_TIME = 0

# Biến lưu trữ UI
root = None
game_overlay = None
move_time_var = None
dao_var = None

_resize_after_id = None
current_scale = 1.0
BASE_WIDTH = 600
BASE_HEIGHT = 620

# =============================
# CLASS LOG REDIRECTOR
# =============================
class TextRedirector:
    def __init__(self, text_widget, q):
        self.text_widget = text_widget
        self.queue = q

    def write(self, msg):
        if msg.strip() != "":
            self.queue.put(msg)

    def flush(self):
        pass


# =============================
# CORE FUNCTIONS
# =============================
def get_move_time():
    """Lấy thời gian di chuyển map từ giao diện một cách an toàn"""
    global move_time_var
    if move_time_var:
        try:
            t = float(move_time_var.get())
            if 0.1 <= t <= 3.0:
                return t
        except:
            pass
    return 0.5  # fallback an toàn


def scan_hanh_quan_periodically(max_dao):
    """
    Định kỳ quét icon hành quân.
    Chỉ reset nếu thiếu đạo LIÊN TIẾP nhiều lần (chống match nhầm).
    """
    global LAST_HANH_QUAN_SCAN, _last_miss_count

    now = time.time()
    if now - LAST_HANH_QUAN_SCAN < HANH_QUAN_INTERVAL:
        return False

    LAST_HANH_QUAN_SCAN = now
    print("\n⏱️ Đến thời điểm quét ICON TỒN TẠI")

    try:
        icon_count = survive.count_survive_icon()
        print(f"🧮 Số icon tồn tại: {icon_count}/{max_dao}")

        # ===== ĐỦ ĐẠO → RESET BỘ ĐẾM =====
        if icon_count >= max_dao:
            _last_miss_count = 0
            print("✅ Đủ đạo → OK")
            return False

        # ===== THIẾU ĐẠO =====
        _last_miss_count += 1
        print(f"⚠️ Thiếu đạo ({_last_miss_count}/{MISS_LIMIT})")

        # ===== THIẾU LIÊN TIẾP → RESET =====
        if _last_miss_count >= MISS_LIMIT:
            print("♻️ Thiếu đạo ổn định → RESET HÀNH QUÂN")
            _last_miss_count = 0
            click_if_hanh_quan()
            return True

    except Exception as e:
        print("❌ Lỗi khi quét survive:", e)

    return False


def check_bug_periodically():
    global LAST_BUG_SCAN_TIME

    now = time.time()
    if now - LAST_BUG_SCAN_TIME < BUG_SCAN_INTERVAL:
        return False  # chưa đến thời điểm scan

    LAST_BUG_SCAN_TIME = now
    print("\n🐞 Đến thời điểm quét BUG")

    result = scan_bug_multi_region()
    if result:
        bug_name = result["bug"]
        bx, by = result["pos"]

        print(f"\n⚠️ Phát hiện BUG: {bug_name} tại ({bx}, {by})")

        # ===== LOGIC CLICK =====
        if bug_name == "lienminh":
            click_x, click_y = 1089 + random.randint(-2, 2), 180 + random.randint(-2, 2)
            print("👉 BUG đặc biệt → click lienminh")
        elif bug_name == "tuido":
            click_x, click_y = 1241 + random.randint(-2, 2), 174 + random.randint(-2, 2)
            print("👉 BUG đặc biệt → click tuido")
        else:
            click_x, click_y = bx, by
            print("👉 BUG thường → click tại vị trí bug")

        like_human.move_mouse_human(click_x, click_y)
        time.sleep(0.2)
        pyautogui.click(click_x, click_y)
        time.sleep(0.5)

        return True

    print("\n✅ Không phát hiện BUG")
    return False


def random_human_click():
    global LAST_RANDOM_CLICK_TIME

    now = time.time()
    if now - LAST_RANDOM_CLICK_TIME < RANDOM_CLICK_INTERVAL:
        return

    LAST_RANDOM_CLICK_TIME = now

    # Xác suất
    if random.random() <= RANDOM_CLICK_PROB:
        print("\n🎲 Random action")
        for _ in range(2):
            like_human.move_mouse_human(random.randint(1363, 1396), random.randint(795, 820))
            time.sleep(random.uniform(0.15, 0.3))
            pyautogui.click()
            time.sleep(random.uniform(0.6, 0.8))


def get_xy(pos, name="unknown"):
    """ Chuẩn hóa dữ liệu (x, y) từ các hàm scan """
    if pos is None:
        return None
    if isinstance(pos, (tuple, list)) and len(pos) == 2:
        return pos[0], pos[1]
    print(f"\n❌ {name} trả dữ liệu sai:", pos, type(pos))
    return None


def avoid_contested_mine(steps=4):
    """ Di chuyển map để né mỏ đang bị tranh """
    directions = ["left", "right", "up", "down"]
    for _ in range(steps):
        direction = random.choice(directions)
        print(f"\n↪ Né mỏ tranh: {direction}")
        move_map.move_one_step(direction, move_time=get_move_time())
        time.sleep(random.uniform(0.4, 0.7))


def find_gem_with_spiral(dao_pos):
    GEM_TIMEOUT = 150
    start_time = time.time()

    spiral = move_map.spiral_step_generator()
    step_index = 0

    dx, dy = dao_pos
    print("\n🌀 Bắt đầu tìm gem (giữ vị trí khi gặp mỏ tranh)")

    while BOT_RUNNING and not BOT_PAUSE:
        # Timeout
        if time.time() - start_time >= GEM_TIMEOUT:
            print("\n⏱️ Timeout → bỏ đạo")
            thu_nho_map()
            time.sleep(0.5)
            return "TIMEOUT"

        # 1️⃣ QUÉT GEM
        gem_pos = scan_gem()
        time.sleep(random.uniform(0.6, 1))
        gem_xy = get_xy(gem_pos, "scan_gem")

        step_index += 1

        if gem_xy:
            gx, gy = gem_xy
            print(f"\n💎 Phát hiện GEM tại bước {step_index}")

            like_human.move_mouse_human(
                gx + random.randint(-2, 2),
                gy + random.randint(-2, 2)
            )
            time.sleep(random.uniform(0.2, 0.4))
            pyautogui.click(
                gx + random.randint(-2, 2),
                gy + random.randint(-2, 2)
            )
            time.sleep(random.uniform(0.5, 1))

            # 2️⃣ KIỂM TRA TRANH
            print("\n🔍 Kiểm tra mỏ tranh")
            tranh_pos = scan_tranh.find_one_image()
            time.sleep(random.uniform(0.6, 1))

            if tranh_pos:
                print("\n⚠️ Mỏ bị tranh → né vị trí này rồi tìm tiếp")
                mo_rong_map()
                time.sleep(0.5)
                # DI CHUYỂN MAP RA KHỎI MỎ BỊ TRANH
                avoid_contested_mine(steps=2)
                # reset spiral sau khi đã di chuyển
                spiral = move_map.spiral_step_generator()
                continue

            # 3️⃣ MỎ TRỐNG → FARM
            print("\n✅ Mỏ trống → kéo farm")
            drag_mouse(dx, dy, gx, gy)
            return "FOUND"

        # 4️⃣ KHÔNG CÓ GEM → DI CHUYỂN
        direction = next(spiral)
        move_map.move_one_step(direction, move_time=get_move_time())


def get_dao_scan_region(dao_index):
    x, y, w, h = DAO_START_REGION
    y = y + (dao_index - 1) * DAO_OFFSET_Y
    return (x, y, w, h)


def bot_loop(max_dao):
    global BOT_RUNNING, BOT_PAUSE

    print("\n🤖 Bot loop start")
    dao_index = 1           # 👉 ĐẠO HIỆN TẠI
    farm_count = 0          # 👉 BIẾN ĐẾM FARM

    while BOT_RUNNING:
        if BOT_PAUSE:
            time.sleep(0.3)
            continue
            
        try:
            check_bug_periodically()
        except Exception as e:
            print("\n❌ Lỗi khi quét bug:", e)
            
        if dao_index > max_dao:
            dao_index = 1   # quay vòng lại đạo 1

        print(f"\n🔎 Quét đạo {dao_index}")
        time.sleep(2)
        scan_region = get_dao_scan_region(dao_index)
        scan_hanh_quan_periodically(max_dao)
        dao_pos = None

        # ===== 1. ƯU TIÊN RETURN =====
        return_pos = scan_return(scan_region)
        ret_xy = get_xy(return_pos, "scan_return")

        if ret_xy:
            print(f"\n↩️ Đạo {dao_index} có RETURN → chỉ dừng, không farm")
            cx, cy = ret_xy
            dao_pos = random_point_in_dao(cx, cy)

            like_human.move_mouse_human(*dao_pos)
            time.sleep(0.3)
            pyautogui.click()
            time.sleep(random.uniform(0.3, 0.5))
            keyboard.press_and_release("s")  # dừng quân
            time.sleep(1)

            # 🔥 BỎ QUA FARM, SANG ĐẠO KHÁC
            dao_index += 1
            continue

        else:
            # ===== 2. CHECK STOP =====
            stop_pos = scan_stop(scan_region)
            time.sleep(random.uniform(0.3, 0.6))
            stop_xy = get_xy(stop_pos, "scan_stop")

            if not stop_xy:
                print(f"❌ Đạo {dao_index} không rảnh")
                dao_index += 1
                time.sleep(0.4)
                continue

            print(f"🟢 Đạo {dao_index} rảnh")
            cx, cy = stop_xy
            dao_pos = random_point_in_dao(cx, cy)

            click_mouse(*dao_pos)
            time.sleep(0.3)

        # ===== 3. TÌM GEM =====
        print("\n🔍 Bắt đầu tìm gem")
        result = find_gem_with_spiral(dao_pos)

        if result == "FOUND":
            farm_count += 1
            print(f"\n✅ Farm xong đạo {dao_index} | Tổng farm: {farm_count}")
            dao_index += 1

        elif result == "TIMEOUT":
            print(f"⏭ Bỏ đạo {dao_index} → sang đạo khác")
            dao_index += 1

        else:
            print("\n🔄 Tiếp tục tìm gem tại đạo hiện tại")

        dao_index += 1
        time.sleep(0.5)

    print("\n⛔ Bot loop stop")


# =============================
# GUI ACTIONS
# =============================
def start_bot():
    global BOT_RUNNING, BOT_PAUSE, dao_var

    if BOT_RUNNING:
        BOT_PAUSE = False
        print("\n▶ Resume bot")
        return

    BOT_RUNNING = True
    BOT_PAUSE = False

    try:
        max_dao = int(dao_var.get())
        if not (1 <= max_dao <= 7):
            raise ValueError
    except:
        print("\n❌ Số đạo không hợp lệ")
        BOT_RUNNING = False
        return

    threading.Thread(
        target=bot_loop,
        args=(max_dao,),
        daemon=True
    ).start()

    print("\n🚀 Bot start")


def pause_bot():
    global BOT_PAUSE
    BOT_PAUSE = True
    print("\n⏸ Bot pause")


def stop_bot():
    global BOT_RUNNING, BOT_PAUSE
    BOT_RUNNING = False
    BOT_PAUSE = False
    print("\n🛑 Bot stop")


def hide_game_overlay():
    global game_overlay
    if game_overlay and game_overlay.winfo_exists():
        game_overlay.destroy()
    game_overlay = None
    print("\n❌ Đã tắt vùng game")


def show_game_overlay():
    global game_overlay

    if game_overlay and game_overlay.winfo_exists():
        print("\nℹ️ Vùng game đang bật")
        return

    game_overlay = tk.Toplevel(root)
    game_overlay.overrideredirect(True)
    game_overlay.attributes("-topmost", True)
    game_overlay.attributes("-alpha", 0.35)

    # CLICK XUYÊN CHUỘT (Windows)
    game_overlay.attributes("-transparentcolor", "black")
    game_overlay.geometry("1440x862+0+0")

    canvas = tk.Canvas(
        game_overlay,
        width=1440,
        height=862,
        bg="black",
        highlightthickness=0
    )
    canvas.pack()

    # 1 KHUNG DUY NHẤT
    canvas.create_rectangle(
        2, 2, 1438, 860,
        outline="lime",
        width=4
    )

    game_overlay.bind("<Escape>", lambda e: hide_game_overlay())
    print("\n🟩 Đã bật vùng game")


# =============================
# SCALING GUI
# =============================
def on_resize(event):
    global _resize_after_id, root
    if root is None or event.widget != root:
        return

    if _resize_after_id:
        root.after_cancel(_resize_after_id)

    _resize_after_id = root.after(
        120,
        lambda: apply_scaling(event.width, event.height)
    )

def apply_scaling(w, h):
    global current_scale, root
    scale_x = w / BASE_WIDTH
    scale_y = h / BASE_HEIGHT
    new_scale = round(min(scale_x, scale_y), 2)
    new_scale = max(0.8, min(new_scale, 1.6))  # giới hạn scale

    if new_scale != current_scale:
        current_scale = new_scale
        try:
            root.tk.call("tk", "scaling", current_scale)
        except:
            pass

# =============================
# ROOT
# =============================
def start_gui():
    global root, dao_var, move_time_var

    root = tk.Tk()
    root.title("💎 ROK GEM FARM BOT")
    
    # Thiết lập kích thước
    root.geometry(f"{BASE_WIDTH}x{BASE_HEIGHT}")
    root.minsize(500, 520)
    root.resizable(True, True)

    root.option_add("*Font", ("Consolas", 12))
    root.tk.call("tk", "scaling", current_scale)
    root.bind("<Configure>", on_resize)

    # Khởi tạo Variables
    move_time_var = tk.StringVar(value="0.5")
    dao_var = tk.StringVar(value="5")

    # =============================
    # STYLE TOÀN CỤC
    # =============================
    style = ttk.Style(root)
    style.configure("Big.TButton", font=("Consolas", 14, "bold"), padding=(24, 16))
    style.configure("TLabelframe.Label", font=("Consolas", 13, "bold"))
    style.configure("TLabel", font=("Consolas", 12))

    # =============================
    # LAYOUT
    # =============================
    main = ttk.Frame(root, padding=12)
    main.pack(fill="both", expand=True)

    # ===== TITLE =====
    ttk.Label(
        main, text="💎 ROK GEM FARM BOT", font=("Consolas", 18, "bold"), anchor="center"
    ).pack(pady=(5, 12))
    ttk.Label(main, text="Vùng game: 1440 x 862", anchor="center").pack(pady=(0, 12))

    # ===== SETTINGS =====
    setting_frame = ttk.LabelFrame(main, text="⚙ Cấu hình", padding=12)
    setting_frame.pack(fill="x", pady=8)

    ttk.Label(setting_frame, text="Số đạo farm (1–7):").grid(row=0, column=0, sticky="w", padx=6, pady=6)
    ttk.Label(setting_frame, text="Thời gian di chuyển map (s):").grid(row=1, column=0, sticky="w", padx=6, pady=6)

    ttk.Entry(setting_frame, width=8, textvariable=dao_var, font=("Consolas", 13)).grid(row=0, column=1, padx=6, pady=6)
    ttk.Entry(setting_frame, width=8, textvariable=move_time_var, font=("Consolas", 13)).grid(row=1, column=1, padx=6, pady=6)

    setting_frame.columnconfigure(2, weight=1)

    # ===== BUTTON BOT =====
    btn_frame = ttk.Frame(main)
    btn_frame.pack(fill="x", pady=12)

    ttk.Button(btn_frame, text="▶ Start / Resume", command=start_bot, style="Big.TButton").grid(row=0, column=0, padx=6, sticky="nsew")
    ttk.Button(btn_frame, text="⏸ Pause", command=pause_bot, style="Big.TButton").grid(row=0, column=1, padx=6, sticky="nsew")
    ttk.Button(btn_frame, text="⛔ Stop", command=stop_bot, style="Big.TButton").grid(row=0, column=2, padx=6, sticky="nsew")

    btn_frame.columnconfigure((0, 1, 2), weight=1)

    # ===== OVERLAY =====
    overlay_frame = ttk.Frame(main)
    overlay_frame.pack(fill="x", pady=8)

    ttk.Button(overlay_frame, text="🟩 Hiện vùng game", command=show_game_overlay, style="Big.TButton").grid(row=0, column=0, padx=6, sticky="nsew")
    ttk.Button(overlay_frame, text="❌ Tắt vùng game", command=hide_game_overlay, style="Big.TButton").grid(row=0, column=1, padx=6, sticky="nsew")

    overlay_frame.columnconfigure((0, 1), weight=1)

    # ===== LOG =====
    log_frame = ttk.LabelFrame(main, text="📜 Log bot", padding=8)
    log_frame.pack(fill="both", expand=True, pady=(12, 0))

    log_text = tk.Text(
        log_frame, bg="black", fg="lime", insertbackground="white",
        state="disabled", wrap="word", font=("Consolas", 11)
    )
    log_text.pack(fill="both", expand=True)

    log_queue = queue.Queue()
    sys.stdout = TextRedirector(log_text, log_queue)
    sys.stderr = TextRedirector(log_text, log_queue)

    def update_log():
        while not log_queue.empty():
            msg = log_queue.get()
            log_text.configure(state="normal")
            log_text.insert("end", msg)
            log_text.see("end")
            log_text.configure(state="disabled")
        root.after(100, update_log)

    update_log()
    root.mainloop()


# CHẠY ỨNG DỤNG TẠI ĐÂY
if __name__ == "__main__":
    start_gui()