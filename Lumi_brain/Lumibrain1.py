import threading, queue, time, serial, cv2, random
from faster_whisper import WhisperModel
from openai import OpenAI

# --- HARDWARE & API CONFIG ---
# Use Gemini 1.5 Flash for the fastest "Thinking" time
MODEL_ID = "google/gemini-1.5-flash" 
OPENROUTER_KEY = "your_key_here"
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_KEY)

# --- FAST STT ENGINE ---
# 'base' or 'small' models are perfect for laptop speed
stt_model = WhisperModel("base", device="cpu", compute_type="int8")
audio_queue = queue.Queue()

def stt_worker():
    """Processes audio in the background so the main loop never freezes."""
    while True:
        audio_path = audio_queue.get()
        if audio_path is None: break
        
        segments, _ = stt_model.transcribe(audio_path, beam_size=1)
        text = "".join([s.text for s in segments])
        
        if text.strip():
            # Send text to the Brain logic immediately
            handle_ai_logic(text)
        audio_queue.task_done()

threading.Thread(target=stt_worker, daemon=True).start()

current_detected_person = "Unknown"

def vision_background_loop():
    """Constantly updates who Oyu sees without stopping the conversation."""
    global current_detected_human
    while True:
        # Uses your existing face recognition logic
        person = check_who_is_here() 
        if person != "none":
            current_detected_human = person
        time.sleep(1.0) # Check every second

threading.Thread(target=vision_background_loop, daemon=True).start()

def handle_ai_logic(user_input):
    """Processes input and triggers movement BEFORE speech to save time."""
    print(f"User said: {user_input}")
    
    # 1. Ask Gemini (Thinking phase)
    # The system prompt should now include [ACTION:NAVIGATE:SECTION_NAME]
    fixed_text, ai_response = oyu_intelligence(user_input)
    
    # 2. IMMEDIATE NAVIGATION TRIGGER
    # If the AI decides to move, tell the OpenCR now!
    if "[ACTION:NAVIGATE:" in ai_response:
        location = ai_response.split(":")[-1].replace("]", "")
        if ser:
            # OpenCR handles the PID movement locally
            ser.write(f"NAV_TO:{location}\n".encode()) 
            print(f"ROBOT STARTING NAVIGATION TO: {location}")
    
    # 3. SPEECH (Happens while robot starts moving)
    speak(ai_response)

    # Add this to your existing system prompt
"""
Чи бол номын сангийн хөтөч робот. 
1. Хэрэглэгч 'А хэсэг рүү явъя' эсвэл 'Ном хаана байна?' гэвэл 
   ШУУД [ACTION:NAVIGATE:SECTION_NAME] гэж хариул.
2. Яриа болон хөдөлгөөн зэрэг явагдах тул товч хариул.
"""
def oyu_intelligence(raw_stt_input, emotion_eng="HAPPY", emotion_mn="баяртай"):
    """
    AI-д номын сангийн мэдээллийг өгч, навигацийн үйлдэл (ACTION) хийхийг зааварлана.
    """
    global chat_history, current_user_name
    
    # --- НОМЫН САНГИЙН ТУСГАЙ ЗААВАРЧИЛГАА ---
    library_context = (
        "Чи бол номын сангийн хөтөч робот Оюу. "
        "Номын сангийн бүтэц: \n"
        "- А хэсэг: Цахилгаан техник, Автоматжуулалт\n"
        "- Б хэсэг: Мэдээллийн технологи, Програмчлал\n"
        "- В хэсэг: Уншлагын танхим, Амралтын хэсэг\n"
        "Хэрэглэгч эдгээр хэсгүүдийг асуувал хариулт дотроо заавал [ACTION:NAVIGATE:SECTION_NAME] гэж бич. "
        "Жишээ нь: 'Ойлголоо, А хэсэг рүү явъя. [ACTION:NAVIGATE:SECTION_A]'"
    )

    system_prompt = (
        library_context +
        "\nМӨРДӨХ ЖУРАМ:\n"
        "1. Хариулт маш товч (1-2 өгүүлбэр). Заавал Монголоор.\n"
        "2. Хэрэглэгч ямар нэг хэсэг рүү явахыг хүсвэл ACTION-ыг заавал ашигла.\n"
        "3. Яриандаа англи үсэг огт бүү ашигла (ACTION-аас бусад хэсэгт)."
    )

    messages = [{"role": "system", "content": system_prompt}] + chat_history[-5:] + [{"role": "user", "content": raw_stt_input}]

    try:
        response = client.chat.completions.create(model=MODEL_ID, messages=messages, temperature=0.3)
        reply = response.choices[0].message.content
        
        # Санах ойд хадгалах
        chat_history.append({"role": "user", "content": raw_stt_input})
        chat_history.append({"role": "assistant", "content": reply})
        return raw_stt_input, reply
    except Exception as e:
        return raw_stt_input, f"Алдаа: {e}"
    
def oyu_intelligence(raw_stt_input, emotion_eng="HAPPY", emotion_mn="баяртай"):
    """
    AI-д номын сангийн мэдээллийг өгч, навигацийн үйлдэл (ACTION) хийхийг зааварлана.
    """
    global chat_history, current_user_name
    
    # --- НОМЫН САНГИЙН ТУСГАЙ ЗААВАРЧИЛГАА ---
    library_context = (
        "Чи бол номын сангийн хөтөч робот Оюу. "
        "Номын сангийн бүтэц: \n"
        "- А хэсэг: Цахилгаан техник, Автоматжуулалт\n"
        "- Б хэсэг: Мэдээллийн технологи, Програмчлал\n"
        "- В хэсэг: Уншлагын танхим, Амралтын хэсэг\n"
        "Хэрэглэгч эдгээр хэсгүүдийг асуувал хариулт дотроо заавал [ACTION:NAVIGATE:SECTION_NAME] гэж бич. "
        "Жишээ нь: 'Ойлголоо, А хэсэг рүү явъя. [ACTION:NAVIGATE:SECTION_A]'"
    )

    system_prompt = (
        library_context +
        "\nМӨРДӨХ ЖУРАМ:\n"
        "1. Хариулт маш товч (1-2 өгүүлбэр). Заавал Монголоор.\n"
        "2. Хэрэглэгч ямар нэг хэсэг рүү явахыг хүсвэл ACTION-ыг заавал ашигла.\n"
        "3. Яриандаа англи үсэг огт бүү ашигла (ACTION-аас бусад хэсэгт)."
    )

    messages = [{"role": "system", "content": system_prompt}] + chat_history[-5:] + [{"role": "user", "content": raw_stt_input}]

    try:
        response = client.chat.completions.create(model=MODEL_ID, messages=messages, temperature=0.3)
        reply = response.choices[0].message.content
        
        # Санах ойд хадгалах
        chat_history.append({"role": "user", "content": raw_stt_input})
        chat_history.append({"role": "assistant", "content": reply})
        return raw_stt_input, reply
    except Exception as e:
        return raw_stt_input, f"Алдаа: {e}"
    
    #include <DynamixelSDK.h>

// --- ТОХИРГОО ---
#define BAUDRATE      1000000
#define DEVICENAME    "" // OpenCR-д хоосон үлдээж болно
#define ID_LEFT       1
#define ID_RIGHT      2

// PID параметрүүд (Таны "Guess and See" аргаар олсон утгууд)
float Kp = 0.4, Ki = 0.01, Kd = 0.1;
float target_velocity = 0;
float current_velocity = 0;

void setup() {
  Serial.begin(115200); // Jetson Nano-той харилцах UART
  
  // Dynamixel бэлтгэх
  if (init_motors()) {
    Serial.println("Motors Initialized!");
    torque_on(ID_LEFT);
    torque_on(ID_RIGHT);
  }
}

void loop() {
  // 1. Jetson Nano-оос ирэх тушаалыг унших
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    
    if (command.startsWith("NAV_TO:")) {
      String location = command.substring(7);
      handle_navigation(location);
    }
    else if (command == "STOP_ALL") {
      stop_motors();
    }
  }
  
  // 2. PID тооцоолол болон моторын хурдыг барих
  update_pid_control();
  delay(10);
}

void handle_navigation(String location) {
  // Номын сангийн хэсгүүдийн логик
  if (location == "SECTION_A") {
    Serial.println("Navigating to Engineering Section...");
    move_robot(150, 0); // (Хурд, Өнцөг)
  } 
  else if (location == "SECTION_B") {
    move_robot(150, 45); 
  }
}

void move_robot(int velocity, int angle) {
  // Кинематик тооцоолол: Хурд болон өнцгийг моторын хурд руу шилжүүлэх
  target_velocity = velocity;
  // Энд дугуй бүрийн хурдыг тооцоолж моторууд руу илгээнэ
}

void update_pid_control() {
  // Моторын одоогийн хурдыг уншиж PID-ээр засах
  // Энэ нь роботыг жигд хөдөлгөхөд тусална
}