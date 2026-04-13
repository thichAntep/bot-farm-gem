import threading
import time
import sys
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import queue
import keyboard
import pyautogui
import random
import ctypes
import requests

# ===== IMPORT BOT MODULE =====
from scan_gem_img import scan_gem
from scan_return_img import scan_return
from scan_stop_img import scan_stop
from scan_is_mine import check_is_mine
from reset_new import click_if_hanh_quan
from farm import drag_mouse
from click_dao import click_mouse, thu_nho_map, mo_rong_map
from choose_dao import random_point_in_dao
import move_map
import scan_tranh
from scan_bug import scan_bug_multi_region
import survive
import like_human
import farm_region
# =======================

def run(username=None, device_id=None):
    # =============================
    # MULTI-LOGIN CHERCKER THREAD
    # =============================
    def heartbeat_thread():
        # URL API để kiểm tra xem device_id hiện tại có còn hợp lệ Không
        API_VERIFY_URL = "https://rok-login-server.onrender.com/api/verify_session"
        while True:
            time.sleep(15)  # Cứ 15 giây ping server báo còn sống / kiểm tra ai đăng nhập máy khác ko
            if username and device_id:
                try:
                    payload = {"username": username, "device_id": device_id}
                    res = requests.post(API_VERIFY_URL, json=payload, timeout=10)
                    if res.status_code == 200:
                        data = res.json()
                        # Nếu server trả về success/valid = false => Bị đăng nhập từ thiết bị khác
                        if data.get("valid") is False or data.get("success") is False:
                            print("\n[!] TÀI KHOẢN ĐÃ ĐƯỢC ĐĂNG NHẬP Ở THIẾT BỊ KHÁC!")
                            global BOT_RUNNING, BOT_PAUSE
                            BOT_RUNNING = False
                            BOT_PAUSE = False
                            
                            try:
                                root.after(0, lambda: [
                                    messagebox.showerror("Bị Đăng Xuất", "Tài khoản của bạn đã được đăng nhập từ một thiết bị khác! Bot sẽ tự đóng."),
                                    os._exit(0)
                                ])
                            except Exception:
                                print("Đóng theo os._exit(0)")
                                os._exit(0)
                            break
                except Exception as e:
                    pass

    if username and device_id:
        threading.Thread(target=heartbeat_thread, daemon=True).start()

    # =============================
    # CONFIG 
    # =============================
    DAO_START_REGION = (1390, 215, 110, 45) # đạo 1
    DAO_OFFSET_Y = 60                       # mỗi đạo lệch 60px
    HANH_QUAN_INTERVAL = 5 * 60             # 5 phút
    MISS_LIMIT = 1                          # thiếu liên tiếp bao nhiêu lần mới reset
    BUG_SCAN_INTERVAL = 3 * 60              # 3 phút
    RANDOM_CLICK_INTERVAL = 2 * 60          # 2 phút
    RANDOM_CLICK_PROB = 0.80                # 80%

    # Global State
    global BOT_RUNNING, BOT_PAUSE, LAST_HANH_QUAN_SCAN, LAST_BUG_SCAN_TIME, LAST_RANDOM_CLICK_TIME, _last_miss_count
    global game_overlay, current_scale, _resize_after_id

    BOT_RUNNING = False
    BOT_PAUSE = False
    LAST_HANH_QUAN_SCAN = 0
    LAST_BUG_SCAN_TIME = 0
    LAST_RANDOM_CLICK_TIME = 0
    _last_miss_count = 0
    game_overlay = None
    current_scale = 1.0
    _resize_after_id = None

    BASE_WIDTH = 600
    BASE_HEIGHT = 650 # Tăng height lên một chút cho vừa cấu hình mới

    print("✅ Bot started thành công (Phiên bản Offline)")

    # ===== REDIRECTOR =====
    class TextRedirector:
        def __init__(self, text_widget, text_queue):
            self.text_widget = text_widget
            self.queue = text_queue

        def write(self, msg):
            if msg.strip() != "":
                self.queue.put(msg)

        def flush(self):
            pass

    # ===== BOT LOGIC FUNCTIONS =====
    def scan_hanh_quan_periodically(max_dao):
        global LAST_HANH_QUAN_SCAN, _last_miss_count
        now = time.time()
        if now - LAST_HANH_QUAN_SCAN < HANH_QUAN_INTERVAL:
            return False

        LAST_HANH_QUAN_SCAN = now
        print("\n⏱️ Đến thời điểm quét ICON TỒN TẠI")
        try:
            icon_count = survive.count_survive_icon()
            print(f"🧮 Số icon tồn tại: {icon_count}/{max_dao}")
            if icon_count >= max_dao:
                _last_miss_count = 0
                print("✅ Đủ đạo → OK")
                return False

            _last_miss_count += 1
            print(f"⚠️ Thiếu đạo ({_last_miss_count}/{MISS_LIMIT})")
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
            return False

        LAST_BUG_SCAN_TIME = now
        print("\n🐞 Đến thời điểm quét BUG")
        result = scan_bug_multi_region()
        if result:
            bug_name = result["bug"]
            bx, by = result["pos"]
            print(f"\n⚠️ Phát hiện BUG: {bug_name} tại ({bx}, {by})")

            if bug_name == "lienminh":
                click_x, click_y = 1089, 180 
            elif bug_name == "tuido":
                click_x, click_y = 1241, 174 
            else:
                click_x, click_y = bx, by

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
        if random.random() <= RANDOM_CLICK_PROB:
            print("\n🎲 Random action")
            for _ in range(2):
                like_human.move_mouse_human(random.randint(1363,1396), random.randint(795,820))
                time.sleep(random.uniform(0.15, 0.3))
                pyautogui.click()
                time.sleep(random.uniform(0.6, 0.8))

    def get_xy(pos, name="unknown"):
        if pos is None:
            return None
        if isinstance(pos, (tuple, list)) and len(pos) == 2:
            return pos[0], pos[1]
        print(f"\n❌ {name} trả dữ liệu sai:", pos, type(pos))
        return None

    def avoid_contested_mine(steps=3):
        directions = ["left", "right", "up", "down"]
        for _ in range(steps):
            direction = random.choice(directions)
            print(f"\n↪ Né mỏ tranh: {direction}")
            move_map.move_one_step(direction, move_time=get_move_time())
            time.sleep(random.uniform(0.4, 0.7))

    def get_move_time():
        try:
            t = float(move_time_var.get())
            if 0.1 <= t <= 3.0:
                return t
        except:
            pass
        return 0.5

    def get_timeout():
        try:
            t = float(timeout_var.get())
            if t > 0:
                return t
        except:
            pass
        return 150.0

    def find_gem_with_spiral(dao_pos):
        GEM_TIMEOUT = get_timeout()
        start_time = time.time()
        spiral = move_map.spiral_step_generator()
        step_index = 0
        dx, dy = dao_pos
        print("\n🌀 Bắt đầu tìm gem (giữ vị trí khi gặp mỏ tranh)")

        while BOT_RUNNING and not BOT_PAUSE:
            if time.time() - start_time >= GEM_TIMEOUT:
                print("\n⏱️ Timeout → bỏ đạo")
                thu_nho_map()
                time.sleep(0.5)
                return "TIMEOUT"

            gem_pos = scan_gem()
            time.sleep(random.uniform(0.6, 1))
            gem_xy = get_xy(gem_pos, "scan_gem")
            step_index += 1

            if gem_xy:
                gx, gy = gem_xy
                print(f"\n💎 Phát hiện GEM tại bước {step_index}")
                like_human.move_mouse_human(gx + random.randint(-2, 2), gy + random.randint(-2, 2))
                time.sleep(random.uniform(0.2, 0.4))
                pyautogui.click(gx + random.randint(-2, 2), gy + random.randint(-2, 2))
                time.sleep(random.uniform(0.5, 1))
                time.sleep(0.8)

                if not check_is_mine():
                    print("\n❌ Không phải mỏ → xử lý như mỏ tranh")
                    mo_rong_map()
                    time.sleep(0.5)
                    avoid_contested_mine(steps=3)
                    spiral = move_map.spiral_step_generator()
                    continue

                print("\n🔍 Kiểm tra mỏ tranh")
                tranh_pos = scan_tranh.find_one_image()
                time.sleep(random.uniform(0.6, 1))
                if tranh_pos:
                    print("\n⚠️ Mỏ bị tranh → né vị trí này rồi tìm tiếp")
                    mo_rong_map()
                    time.sleep(0.5)
                    avoid_contested_mine(steps=3)
                    spiral = move_map.spiral_step_generator()
                    continue

                print("\n✅ Mỏ trống → kéo farm")
                drag_mouse(dx, dy, gx, gy)
                return "FOUND"

            direction = next(spiral)
            move_map.move_one_step(direction, move_time=get_move_time())

    def get_dao_scan_region(dao_index):
        x, y, w, h = DAO_START_REGION
        y = y + (dao_index - 1) * DAO_OFFSET_Y
        return (x, y, w, h)

    def bot_loop(max_dao):
        global BOT_RUNNING, BOT_PAUSE
        print("\n🤖 Bot loop start")
        dao_index = 1
        farm_count = 0

        while BOT_RUNNING:
            if BOT_PAUSE:
                time.sleep(0.3)
                continue
            try:
                check_bug_periodically()
            except Exception as e:
                print("\n❌ Lỗi khi quét bug:", e)
                
            if dao_index > max_dao:
                dao_index = 1

            print(f"\n🔎 Quét đạo {dao_index}")
            time.sleep(2)
            scan_region = get_dao_scan_region(dao_index)
            scan_hanh_quan_periodically(max_dao)
            
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
                keyboard.press_and_release("s")
                time.sleep(1)
                dao_index += 1
                continue
            else:
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
                
                # === THÊM MODULE MỚI: Di chuyển đến farm region ===
                if use_farm_region_var.get():
                    print(f"🚜 Đang đưa đạo {dao_index} đến khu vực farm...")
                    try:
                        farm_region.farm_region(dao_index)
                    except Exception as e:
                        print(f"❌ Lỗi khi di chuyển region: {e}")
                else:
                    print(f"⏩ Bỏ qua di chuyển region do đã tắt trong Cấu hình.")
                # ==================================================

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

    # ===== BOT CONTROL FUNCTIONS =====
    def start_bot():
        global BOT_RUNNING, BOT_PAUSE
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
            
        # Cập nhật tọa độ farm region nếu được bật
        if use_farm_region_var.get():
            coords_dict = {}
            for i in range(max_dao):
                try:
                    cx = int(dao_x_vars[i].get())
                    cy = int(dao_y_vars[i].get())
                    coords_dict[i+1] = (cx, cy)
                except Exception as e:
                    print(f"Lỗi đọc tọa độ đạo {i+1}, dùng mặc định (0,0)")
                    coords_dict[i+1] = (0, 0)
            farm_region.set_farm_coordinates(coords_dict)
            print(f"\n✅ Đã truyền tọa độ farm cho {max_dao} đạo.")

        threading.Thread(target=bot_loop, args=(max_dao,), daemon=True).start()
        print("\n🚀 Bot started")

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
        canvas.create_rectangle(4, 4, 1438, 860, outline="#FFFF00", width=15)
        game_overlay.bind("<Escape>", lambda e: hide_game_overlay())
        print("\n🟩 Đã bật vùng game")

    def apply_scaling(w, h):
        global current_scale
        scale = min(w / BASE_WIDTH, h / BASE_HEIGHT)
        scale = max(0.8, min(scale, 1.6))
        if scale != current_scale:
            current_scale = scale
            root.tk.call("tk", "scaling", current_scale)

    def on_resize(event):
        global _resize_after_id
        if event.widget != root:
            return
        if _resize_after_id:
            root.after_cancel(_resize_after_id)
        _resize_after_id = root.after(120, lambda: apply_scaling(event.width, event.height))

    # =============================
    # GUI INITIALIZATION
    # =============================
    root = tk.Tk()
    root.title("💎 ROK GEM FARM BOT")
    root.configure(bg="red")

    style = ttk.Style(root)
    style.configure("Big.TButton", font=("Consolas", 14, "bold"), padding=(24, 16))
    style.configure("TLabelframe.Label", font=("Consolas", 13, "bold"))
    style.configure("TLabel", font=("Consolas", 12))

    root.geometry(f"{BASE_WIDTH}x{BASE_HEIGHT}")
    root.minsize(500, 520)
    root.resizable(True, True)
    root.tk.call("tk", "scaling", 1.0)
    root.option_add("*Font", ("Consolas", 12))
    root.bind("<Configure>", on_resize)

    main = ttk.Frame(root, padding=12)
    main.pack(fill="both", expand=True)

    ttk.Label(main, text="💎 Đào Gem ", font=("Consolas", 18, "bold"), anchor="center").pack(pady=(5, 12))
    ttk.Label(main, text="Vùng game: 1440 x 862", anchor="center").pack(pady=(0, 12))

    # Khai báo biến
    move_time_var = tk.StringVar(value="0.5")
    timeout_var = tk.StringVar(value="150")
    dao_var = tk.StringVar(value="5")
    use_farm_region_var = tk.BooleanVar(value=True) # Biến cho chức năng bật/tắt module farm_region

    setting_frame = ttk.LabelFrame(main, text="⚙ Cấu hình", padding=12)
    setting_frame.pack(fill="x", pady=8)
    
    ttk.Label(setting_frame, text="Số đạo farm (1–7):").grid(row=0, column=0, sticky="w", padx=6, pady=6)
    ttk.Entry(setting_frame, width=8, textvariable=dao_var, font=("Consolas", 13)).grid(row=0, column=1, padx=6, pady=6)
    
    ttk.Label(setting_frame, text="Thời gian di chuyển map (s):").grid(row=1, column=0, sticky="w", padx=6, pady=6)
    ttk.Entry(setting_frame, width=8, textvariable=move_time_var, font=("Consolas", 13)).grid(row=1, column=1, padx=6, pady=6)
    
    ttk.Label(setting_frame, text="Thời gian 1 đạo tìm gem (s):").grid(row=2, column=0, sticky="w", padx=6, pady=6)
    ttk.Entry(setting_frame, width=8, textvariable=timeout_var, font=("Consolas", 13)).grid(row=2, column=1, padx=6, pady=6)

    # === GIAO DIỆN MỚI THÊM ===
    ttk.Label(setting_frame, text="Bật đi farm khu vực (Farm Region):").grid(row=3, column=0, sticky="w", padx=6, pady=6)
    ttk.Checkbutton(setting_frame, variable=use_farm_region_var, text="Bật / Tắt").grid(row=3, column=1, sticky="w", padx=6, pady=6)
    # ==========================

    setting_frame.columnconfigure(2, weight=1)

    # --- Frame cấu hình tọa độ cho từng đạo ---
    farm_coord_frame = ttk.LabelFrame(main, text="📍 Tọa độ Vùng Farm", padding=12)
    farm_coord_frame.pack(fill="x", pady=8)
    
    global dao_x_vars, dao_y_vars
    dao_x_vars = []
    dao_y_vars = []
    
    # Tạo sẵn 7 dòng nhập liệu cho 7 đạo
    for i in range(7):
        ttk.Label(farm_coord_frame, text=f"Đạo {i+1} : X =").grid(row=i//2, column=(i%2)*4, sticky="e", padx=(10, 2), pady=4)
        x_var = tk.StringVar(value="0")
        ttk.Entry(farm_coord_frame, width=5, textvariable=x_var, font=("Consolas", 11)).grid(row=i//2, column=(i%2)*4 + 1, padx=2, pady=4)
        dao_x_vars.append(x_var)
        
        ttk.Label(farm_coord_frame, text="Y =").grid(row=i//2, column=(i%2)*4 + 2, sticky="e", padx=(5, 2), pady=4)
        y_var = tk.StringVar(value="0")
        ttk.Entry(farm_coord_frame, width=5, textvariable=y_var, font=("Consolas", 11)).grid(row=i//2, column=(i%2)*4 + 3, sticky="w", padx=2, pady=4)
        dao_y_vars.append(y_var)

    def auto_fill_coords():
        try:
            base_x = int(dao_x_vars[0].get())
            base_y = int(dao_y_vars[0].get())
            for idx in range(1, 7):
                dao_x_vars[idx].set(str(base_x - idx * 50))
                dao_y_vars[idx].set(str(base_y - idx * 50))
            print("\n✅ Đã điền nhanh tọa độ cho các đạo còn lại!")
        except ValueError:
            print("\n❌ Vui lòng nhập tọa độ hợp lệ cho Đạo 1 trước khi bấm điền nhanh.")

    ttk.Button(farm_coord_frame, text="⚡ Điền nhanh (từ Đạo 1, trừ 50)", command=auto_fill_coords).grid(row=4, column=0, columnspan=8, pady=(10, 0))

    def toggle_farm_coord_frame(*args):
        if use_farm_region_var.get():
            try:
                farm_coord_frame.pack(fill="x", pady=8, before=btn_frame)
            except tk.TclError:
                farm_coord_frame.pack(fill="x", pady=8)
        else:
            farm_coord_frame.pack_forget()

    use_farm_region_var.trace_add("write", toggle_farm_coord_frame)

    btn_frame = ttk.Frame(main)
    btn_frame.pack(fill="x", pady=12)
    ttk.Button(btn_frame, text="▶ Start / Resume", command=start_bot, style="Big.TButton").grid(row=0, column=0, padx=6, sticky="nsew")
    ttk.Button(btn_frame, text="⏸ Pause", command=pause_bot, style="Big.TButton").grid(row=0, column=1, padx=6, sticky="nsew")
    ttk.Button(btn_frame, text="⛔ Stop", command=stop_bot, style="Big.TButton").grid(row=0, column=2, padx=6, sticky="nsew")
    btn_frame.columnconfigure((0, 1, 2), weight=1)

    overlay_frame = ttk.Frame(main)
    overlay_frame.pack(fill="x", pady=8)
    ttk.Button(overlay_frame, text="🟩 Hiện vùng game", command=show_game_overlay, style="Big.TButton").grid(row=0, column=0, padx=6, sticky="nsew")
    ttk.Button(overlay_frame, text="❌ Tắt vùng game", command=hide_game_overlay, style="Big.TButton").grid(row=0, column=1, padx=6, sticky="nsew")
    overlay_frame.columnconfigure((0, 1), weight=1)

    log_frame = ttk.LabelFrame(main, text="📜 Log bot", padding=8)
    log_frame.pack(fill="both", expand=True, pady=(12, 0))

    log_text = tk.Text(log_frame, bg="black", fg="lime", insertbackground="white", state="disabled", wrap="word", font=("Consolas", 11))
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

# Điểm neo để file chạy trực tiếp khi bấm Play / hoặc build file exe
if __name__ == "__main__":
    run()