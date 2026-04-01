import os
import sys
import cv2
import numpy as np
import pyautogui

# 1. THIẾT LẬP MÔI TRƯỜNG NGAY LẬP TỨC TRƯỚC KHI IMPORT TORCH
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1" # Ép CPU chỉ dùng 1 luồng để tránh lỗi xung đột bộ nhớ

model = None

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        # Khi chạy bằng file .exe
        base_path = os.path.dirname(sys.executable)
    else:
        # Khi chạy bằng file .py
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_model():
    global model
    if model is None:
        print("🔄 Loading model...")
        
        # 2. ĐƯA IMPORT VÀO TRONG HÀM
        # Đảm bảo torch chỉ được gọi sau khi os.environ đã kích hoạt
        import torch
        from ultralytics import YOLO
        
        torch.set_num_threads(1)
        
        model_path = resource_path("best.pt") 
        
        # Thêm check để báo lỗi rõ ràng nếu quên copy file best.pt
        if not os.path.exists(model_path):
            print(f"❌ LỖI: Không tìm thấy file {model_path}!")
            print("Vui lòng copy file best.pt để cùng thư mục với file .exe")
            sys.exit(1)
            
        model = YOLO(model_path, task='detect') # Ép task='detect' cho an toàn
        # model.to("cpu") # Không cần thiết vì YOLO tự động nhận diện CPU nếu không có CUDA
        print("✅ Model loaded successfully on CPU")

SCAN_REGION = (100,50,1200,700)
CONF_THRESHOLD = 0.1

def scan_gem():
    load_model()

    screenshot = pyautogui.screenshot(region=SCAN_REGION)
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    # Đưa ảnh vào model (đảm bảo import không bị gọi ra ngoài)
    results = model(frame, conf=CONF_THRESHOLD, device="cpu", verbose=False)

    best_point = None
    best_dist = 999999

    for r in results:
        for box in r.boxes:
            x1,y1,x2,y2 = box.xyxy[0].cpu().numpy() # Ép về numpy mảng an toàn

            cx = int((x1+x2)/2)
            cy = int((y1+y2)/2)

            dist = (cx-720)**2 + (cy-430)**2

            if dist < best_dist:
                best_dist = dist
                real_x = cx + SCAN_REGION[0]
                real_y = cy + SCAN_REGION[1]
                best_point = (real_x, real_y)

    return best_point