import serial
import time

# --- ЦУВАА ХОЛБООНЫ ТОХИРГОО (Serial Config) ---
# Jetson Nano дээрх UART портыг зааж өгнө (Жишээ нь: /dev/ttyTHS1 эсвэл /dev/ttyUSB0)
# Лаптоп дээр бол 'COM3' гэх мэт байна
SERIAL_PORT = "/dev/ttyS1" 
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"[Nav Planner] OpenCR-тэй {SERIAL_PORT} портоор холбогдлоо.")
except Exception as e:
    print(f"[Nav Planner] Анхааруулга: OpenCR холбогдсонгүй. Симуляцийн горимд шилжлээ. ({e})")
    ser = None

def send_navigation_command(ai_response):
    """
    AI-ийн хариулт доторх [ACTION:NAVIGATE:...] тушаалыг хайж олоод 
    OpenCR рүү илгээнэ.
    """
    if "[ACTION:NAVIGATE:" in ai_response:
        # Жишээ: "[ACTION:NAVIGATE:SECTION_A]" гэдгээс "SECTION_A"-г салгаж авах
        parts = ai_response.split("ACTION:NAVIGATE:")
        if len(parts) > 1:
            location = parts[1].split("]")[0].strip()
            
            print(f"[Nav Planner] 🚀 Робот хөдөлж эхэллээ. Чиглэл: {location}")
            
            if ser:
                # OpenCR-рүү комманд илгээх
                command = f"NAV_TO:{location}\n"
                ser.write(command.encode('utf-8'))
            else:
                print(f"[Nav Planner] (Симуляци) {location} руу хөдөлгүүрийн тушаал илгээгдлээ.")