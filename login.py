import tkinter as tk
from tkinter import messagebox
import requests
import subprocess
import sys
import os
import platform
import uuid

# Thay thế URL này bằng URL API thực tế trên server Render của bạn
API_URL = "https://rok-login-server.onrender.com/api/login"

def get_device_id():
    try:
        if platform.system() == "Windows":
            output = subprocess.check_output('wmic csproduct get uuid', shell=True).decode().split('\n')[1].strip()
            if output: return output
    except:
        pass
    return str(uuid.getnode())

DEVICE_ID = get_device_id()

def attempt_login():
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ tài khoản và mật khẩu!")
        return

    try:
        # Gửi request lên server Render để kiểm tra thông tin, kèm thiết bị (device_id)
        # Bạn cần chỉnh server API lưu lại device_id mới nhất của tài khoản này
        payload = {
            "username": username, 
            "password": password,
            "device_id": DEVICE_ID
        }
        response = requests.post(API_URL, json=payload, timeout=100)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") or data.get("status") == "ok":
                messagebox.showinfo("Thành công", "Đăng nhập thành công!")
                root.destroy()  # Đóng cửa sổ đăng nhập
                start_main_bot(username, DEVICE_ID)
            else:
                messagebox.showerror("Thất bại", "Tài khoản hoặc mật khẩu không chính xác!")
        else:
            messagebox.showerror("Lỗi Server", f"Lỗi từ server (Code: {response.status_code})")
            
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Lỗi Kết Nối", "Không thể kết nối đến server. Vui lòng kiểm tra lại mạng hoặc server!")

def start_main_bot(username, device_id):
    try:
        import main
        main.run(username, device_id)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể khởi chạy bot chính:\n{e}")


# Thiết lập giao diện
root = tk.Tk()
root.title("Đăng Nhập Bot")
root.geometry("350x250")
root.resizable(False, False)

# Code để căn giữa cửa sổ trên màn hình
root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

# Label tiêu đề
lbl_title = tk.Label(root, text="ĐĂNG NHẬP HỆ THỐNG", font=("Arial", 14, "bold"))
lbl_title.pack(pady=20)

# Frame chứa form
frame_form = tk.Frame(root)
frame_form.pack()

# Username
tk.Label(frame_form, text="Tài khoản:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_username = tk.Entry(frame_form, width=25, font=("Arial", 10))
entry_username.grid(row=0, column=1, padx=5, pady=5)

# Password
tk.Label(frame_form, text="Mật khẩu:", font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_password = tk.Entry(frame_form, show="*", width=25, font=("Arial", 10))
entry_password.grid(row=1, column=1, padx=5, pady=5)

# Nút Đăng nhập
btn_login = tk.Button(root, text="Đăng Nhập", font=("Arial", 10, "bold"), bg="#000000", fg="white", command=attempt_login, width=15)
btn_login.pack(pady=20)

# Bind phím Enter để đăng nhập
root.bind('<Return>', lambda event: attempt_login())

root.mainloop()
