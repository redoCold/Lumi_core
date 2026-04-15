import cv2
import time
import threading

# --- ДАЛД ХУВЬСАГЧИД (Global State) ---
# Камер хэнийг харж байгааг энд байнга шинэчилж хадгална
current_detected_person = "Unknown"

def check_who_is_here():
    """
    Таны өмнөх код дахь нүүр таних үндсэн функц.
    Камер асааж, хүн байгаа эсэхийг шалгана.
    """
    # Жич: Энд та өөрийн LBPHFaceRecognizer болон haarcascade кодоо оруулна
    # Одоогоор камерын ажиллагааг дуурайлгаж байна
    
    cap = cv2.VideoCapture(1) # Буруу порт байвал 0 болгож өөрчилнө
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
        
    # Хэрэв камер ажиллахгүй бол алдаа буцаана
    if not cap.isOpened():
        return "error"
        
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        # Энд царай таних логик ажиллаад нэр буцаана гэж үзэе
        # found_name = "Бат" 
        return "none" # Түр хугацаанд "хэн ч алга" гэж буцааж байна
    else:
        return "none"

def vision_background_loop():
    """
    Далд ажиллах процесс: 1 секунд тутамд камер руу шалгаж, 
    хэн байгааг шинэчилнэ.
    """
    global current_detected_person
    while True:
        person = check_who_is_here()
        
        # Зөвхөн хүн олдсон үед л хувьсагчийг шинэчилнэ
        if person not in ["none", "error"]:
            current_detected_person = person
            
        time.sleep(1.0) # Системийг гацаахгүйн тулд 1 секунд амарна

def start_vision_engine():
    """
    Vision Thread-ийг асаах функц. Үүнийг Lumibrain1.py-аас дуудна.
    """
    vision_thread = threading.Thread(target=vision_background_loop, daemon=True)
    vision_thread.start()
    print("[Vision Engine] Камерын модуль далд ажиллаж эхэллээ.")

def get_current_person():
    """
    AI-ийн тархи хэн байгааг мэдэхийг хүсвэл энэ функцийг дуудна.
    """
    return current_detected_person