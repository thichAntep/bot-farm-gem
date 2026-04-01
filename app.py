import os
import sys

# =====================================================================
# BẮT BUỘC ĐẶT ĐOẠN NÀY LÊN ĐẦU TIÊN (TRƯỚC KHI IMPORT CÁC FILE KHÁC)
# Để trị dứt điểm lỗi WinError 1114 (c10.dll) của PyTorch
# =====================================================================
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

if getattr(sys, 'frozen', False):
    # Trỏ thẳng vào thư mục chứa dll của torch trong file build
    internal_dir = sys._MEIPASS 
    torch_lib_dir = os.path.join(internal_dir, 'torch', 'lib')
    
    if os.path.exists(torch_lib_dir):
        os.add_dll_directory(torch_lib_dir)
# =====================================================================


# BÂY GIỜ MỚI ĐƯỢC IMPORT CÁC FILE CỦA BẠN VÀO
import bot_login
import chorme

def main():
    token = bot_login.show_login()

    if not token:
        print("❌ Login thất bại")
        return

    chorme.run(token)

if __name__ == "__main__":
    main()