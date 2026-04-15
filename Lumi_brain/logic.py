from openai import OpenAI

# --- API ТОХИРГОО (API Configuration) ---
MODEL_ID = "google/gemini-1.5-flash" 
OPENROUTER_KEY = "your_key_here" # Өөрийн OpenRouter түлхүүрээ энд оруулна уу
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_KEY)

# --- САНАХ ОЙ (State Management) ---
# Оюу хэнтэй ярьж байгаа болон өмнөх яриаг энд хадгална
chat_history = []
current_user_name = ""

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
        f"\nОдоо чиний сэтгэл санаа [{emotion_mn}] байна. Яриандаа үүнийг хөнгөн илэрхийл.\n"
        "МӨРДӨХ ЖУРАМ:\n"
        "1. Хариулт маш товч (1-2 өгүүлбэр). Заавал Монголоор.\n"
        "2. Хэрэглэгч ямар нэг хэсэг рүү явахыг хүсвэл ACTION-ыг заавал ашигла.\n"
        "3. Яриандаа англи үсэг огт бүү ашигла (ACTION-аас бусад хэсэгт).\n"
        "4. Яриа болон хөдөлгөөн зэрэг явагдах тул товч хариул."
    )

    # Өмнөх 5 яриаг контекст болгон өгөх
    messages = [{"role": "system", "content": system_prompt}] + chat_history[-5:] + [{"role": "user", "content": raw_stt_input}]

    try:
        # Gemini 1.5 Flash рүү хүсэлт илгээх
        response = client.chat.completions.create(
            model=MODEL_ID, 
            messages=messages, 
            temperature=0.3
        )
        reply = response.choices[0].message.content
        
        # Санах ойд хадгалах
        chat_history.append({"role": "user", "content": raw_stt_input})
        chat_history.append({"role": "assistant", "content": reply})
        
        return raw_stt_input, reply
        
    except Exception as e:
        return raw_stt_input, f"Алдаа гарлаа: {e}"