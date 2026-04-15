import speech_recognition as sr
import time
import time
# Бусад модулиудаа оруулж ирэх
from logic import oyu_intelligence
from stt_engine import start_stt_engine, add_audio_to_queue
from vision import start_vision_engine, get_current_person
from nav_planner import send_navigation_command

# --- МИКРОФОНЫ ТОХИРГОО (Microphone Setup) ---
recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.5  # 0.5 секунд дуугүй болоход шууд бичлэгийг зогсооно (Хурдыг нэмэгдүүлнэ)

def listen_and_save():
    """
    Микрофоноос дуу бичиж аваад 'input.wav' файл болгон хадгална.
    """
    # Хэрэв танд олон микрофон байгаад бурууг нь сонсоод байвал sr.Microphone(device_index=2) гэж сольж болно
    with sr.Microphone() as source: 
        print("\n[🎙️] Оюу сонсож байна...")
        
        # Орчны чимээг маш хурдан (0.2s) шалгаж шүүх
        recognizer.adjust_for_ambient_noise(source, duration=0.2) 
        
        try:
            # timeout=3: 3 секунд хэн ч юу ч хэлэхгүй бол зогсоно
            # phrase_time_limit=10: Нэг өгүүлбэр дээд тал нь 10 секунд байна
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=10)
            
            # Үргэлж нэг ижил нэртэй файл дээр дарж бичнэ (Хатуу диск дүүрэхээс сэргийлнэ)
            file_name = "input.wav"
            with open(file_name, "wb") as f:
                f.write(audio.get_wav_data())
                
            print("[✅] Дуу хүлээж авлаа. Дараалал руу шилжүүлэв.")
            return file_name
            
        except sr.WaitTimeoutError:
            # Чимээгүй байвал ямар нэг алдаа заахгүйгээр буцаах
            return None
        except Exception as e:
            print(f"[Микрофон алдаа]: {e}")
            return None
        
def speak(text):
    """Энд өөрийн SonurTTS эсвэл өөр TTS кодоо дуудна.
    Цэвэрлэх: ACTION тагуудыг устгаад зөвхөн ярих текстийг үлдээнэ."""
    import re
    clean_text = re.sub(r'\[ACTION.*?\]', '', text).strip()
    print(f"\n[Оюу]: {clean_text}\n")
    
def ai_callback(transcribed_text):
    """STT хөдөлгүүр аудиог текст болгож дуусмагц энэ функц автоматаар ажиллана."""
    print(f"[Та]: {transcribed_text}")
    # 1. Тархи руу илгээж бодуулах
    _, ai_response = oyu_intelligence(transcribed_text)
    # 2. Хэрэв хөдлөх шаардлагатай бол моторт тушаал өгөх (Ярьж эхлэхээс өмнө)
    send_navigation_command(ai_response)
    # 3. Хариулах (Хөдөлж байхдаа ярина)
    speak(ai_response)

if __name__ == "__main__":
    print("=== Lumi Core Subsystems Эхэлж байна ===")
    # 1. Далд процессуудыг асаах (Нүд болон Чих)
    start_vision_engine()
    start_stt_engine(ai_callback) # STT-д өөрийн callback функцийг өгнө
    print("=== Оюу ажиллахад бэлэн боллоо ===")
    # 2. Үндсэн гогцоо (Микрофон байнга сонсож байх хэсэг)
    while True:
        try:
            # Микрофоныг асааж сонсох
            audio_file = listen_and_save()
            # Хэрэв дуу амжилттай бичигдсэн бол STT хөдөлгүүр рүү илгээх
            if audio_file:
                add_audio_to_queue(audio_file)
            time.sleep(0.1) # Системийг хэт ачааллахаас сэргийлнэ
        except KeyboardInterrupt:
            print("\nПрограмм зогслоо.")
            break