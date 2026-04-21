import threading
import queue
from faster_whisper import WhisperModel
# --- АУДИО ДАРААЛАЛ (Task Queue) ---
audio_queue = queue.Queue()
# --- МОДЕЛЬ АЧААЛАХ ---
print("[STT Engine] Faster-Whisper working. Түр хүлээнэ үү...")
stt_model = WhisperModel("base", device="cpu", compute_type="int8")

def stt_worker(on_text_ready_callback):
    """Далд ажиллах процесс: Queue-д аудио орж ирэхийг хүлээж байгаад,
    орж ирмэгц нь текст рүү хөрвүүлээд Main Logic рүү илгээнэ."""
    while True:
        audio_path = audio_queue.get()
        if audio_path is None: 
            break
        #audio to text here
        segments, _ = stt_model.transcribe(audio_path, beam_size=1)
        text = "".join([s.text for s in segments])
        
        #Хэрэв чимээгүй биш, ямар нэг үг сонсогдсон бол
        if text.strip():
            #Олдсон текстийг Үндсэн программ руу (Lumibrain1.py) буцааж илгээх
            on_text_ready_callback(text)
            
        audio_queue.task_done()

def start_stt_engine(callback_function):
    """STT Thread-ийг асаах функц. Үүнийг Lumibrain1.py-аас дуудна."""
    stt_thread = threading.Thread(target=stt_worker, args=(callback_function,), daemon=True)
    stt_thread.start()
    print("[STT Engine] Сонсох модуль амжилттай ажиллаж эхэллээ.")

def add_audio_to_queue(file_path):
    """Бичигдсэн аудио файлыг дараалалд оруулах функц."""
    audio_queue.put(file_path)
    