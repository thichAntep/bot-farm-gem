import tkinter as tk
import requests
import uuid

SERVER = "http://104.214.187.65:5000"

def get_hwid():
    return hex(uuid.getnode())

def show_login():
    result = {"token": None}

    def do_login():
        username = entry_user.get()
        password = entry_pass.get()

        try:
            r = requests.post(
                SERVER + "/login",
                json={
                    "username": username,
                    "password": password,
                    "hwid": get_hwid()
                }
            )

            data = r.json()
        except:
            status.config(text="Server offline")
            return

        if data["status"] != "success":
            status.config(text="Login fail")
            return

        result["token"] = data["token"]
        root.destroy()

    root = tk.Tk()
    root.title("Login")

    tk.Label(root, text="Username").pack()
    entry_user = tk.Entry(root)
    entry_user.pack()

    tk.Label(root, text="Password").pack()
    entry_pass = tk.Entry(root, show="*")
    entry_pass.pack()

    tk.Button(root, text="Login", command=do_login).pack()

    status = tk.Label(root, text="")
    status.pack()

    root.mainloop()

    return result["token"]