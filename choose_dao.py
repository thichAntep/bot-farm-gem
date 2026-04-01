import math
import random

def random_point_in_dao(Cx, Cy):
    """
    Hàm tính tọa độ click dựa trên phép tịnh tiến mẫu từ A -> Ao.
    Áp dụng cho mọi cặp Cx, Cy đầu vào.
    """
    # ==========================================
    # 1. DỮ LIỆU THAM CHIẾU (Bạn cung cấp)
    # ==========================================
    # Tọa độ A ban đầu
    A_ref_x, A_ref_y = 1411, 358
    
    # Tọa độ Ao đích (tâm hình tròn)
    Ao_ref_x, Ao_ref_y = 1399, 345
    
    # Bán kính vùng random
    RADIUS = 3

    # ==========================================
    # 2. TÍNH TOÁN
    # ==========================================
    
    # Bước A: Tính độ lệch tịnh tiến (Vector dịch chuyển)
    # Công thức: Đích - Gốc
    offset_x = Ao_ref_x - A_ref_x  # 1399 - 1411 = -12
    offset_y = Ao_ref_y - A_ref_y  # 345 - 358 = -13

    # Bước B: Áp dụng độ lệch này vào tọa độ input (Cx, Cy) để tìm tâm mới
    center_x = Cx + offset_x
    center_y = Cy + offset_y

    # Bước C: Lấy ngẫu nhiên 1 điểm trong hình tròn bán kính 13px tại tâm mới
    # Góc ngẫu nhiên từ 0 đến 360 độ (2*pi)
    angle = random.uniform(0, 2 * math.pi)
    
    # Khoảng cách từ tâm (dùng sqrt để điểm phân bố đều, không bị tụ vào giữa)
    distance = RADIUS * math.sqrt(random.random())

    # Tính tọa độ cuối cùng
    final_x = center_x + distance * math.cos(angle)
    final_y = center_y + distance * math.sin(angle)

    # Trả về số nguyên (pixel)
    return int(final_x), int(final_y)