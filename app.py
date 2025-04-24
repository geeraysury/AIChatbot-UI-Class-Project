import gradio as gr
import os
from groq import Groq

api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

conversation_history = []

LANGUAGES = {
    "English": "en",
    "Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko",
    "Hindi": "hi",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
}

TRANSLATIONS = {
    "en": {  # English
        "title": "ResumeGenie",
        "placeholder": "How can we help with your resume?",
        "change_lang": "Change Language",
        "clear": "🗑 Clear",
        "enter": "Enter",
        "voice_label": "Voice Recognition Chat",
    },
    "es": {  # Spanish
        "title": "ResumeGenie",
        "placeholder": "¿Cómo podemos ayudarte con tu currículum?",
        "change_lang": "Cambiar Idioma",
        "clear": "🗑 Limpiar",
        "enter": "Enviar",
        "voice_label": "Chat de Reconocimiento de Voz",
    },
    "fr": {  # French
        "title": "ResumeGenie",
        "placeholder": "Comment pouvons-nous vous aider avec votre CV ?",
        "change_lang": "Changer de Langue",
        "clear": "🗑 Effacer",
        "enter": "Envoyer",
        "voice_label": "Chat de Reconnaissance Vocale",
    },
    "de": {  # German
        "title": "ResumeGenie",
        "placeholder": "Wie können wir Ihnen mit Ihrem Lebenslauf helfen?",
        "change_lang": "Sprache ändern",
        "clear": "🗑 Löschen",
        "enter": "Senden",
        "voice_label": "Spracherkennungs-Chat",
    },
    "zh": {  # Chinese (Simplified)
        "title": "简历精灵",
        "placeholder": "我们如何帮助您优化简历？",
        "change_lang": "更改语言",
        "clear": "🗑 清除",
        "enter": "发送",
        "voice_label": "语音识别聊天",
    },
    "ja": {  # Japanese
        "title": "履歴書ジェニー",
        "placeholder": "履歴書についてどのようにお手伝いできますか？",
        "change_lang": "言語を変更",
        "clear": "🗑 クリア",
        "enter": "送信",
        "voice_label": "音声認識チャット",
    },
    "ko": {  # Korean
        "title": "이력서 지니",
        "placeholder": "이력서와 관련하여 어떻게 도와드릴까요?",
        "change_lang": "언어 변경",
        "clear": "🗑 지우기",
        "enter": "보내기",
        "voice_label": "음성 인식 채팅",
    },
    "hi": {  # Hindi
        "title": "रिज्यूम जिनी",
        "placeholder": "हम आपके रिज्यूमे में कैसे मदद कर सकते हैं?",
        "change_lang": "भाषा बदलें",
        "clear": "🗑 साफ करें",
        "enter": "भेजें",
        "voice_label": "वॉइस रिकग्निशन चैट",
    },
}

def chat_with_bot_stream(user_input):
    global conversation_history

    # Ensure history persists correctly
    if not conversation_history:
        conversation_history.append({"role": "system", "content": """
            You are an expert resume assistant specializing in optimizing resumes for job seekers of all experience levels.
            Your goal is to enhance resumes according to industry standards.
        """})

    # Append user message
    conversation_history.append({"role": "user", "content": user_input})

    # AI completion
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        temperature=0.62,
        messages=conversation_history,  # Pass conversation history
        max_completion_tokens=1024,
        top_p=0.9,
        stream=False,  # Make sure streaming doesn't break multi-turn conversations
        stop=None,
    )

    # Get response
    response_content = completion.choices[0].message.content

    # Append AI response
    conversation_history.append({"role": "assistant", "content": response_content})

    return response_content
    
def fix_resume(resume_text):
    messages = [
        {
            "role": "system",
            "content": """
            You are a professional resume expert. Your job is to improve, reformat, and optimize resumes to be ATS-friendly, clear, and professional. 
            Follow these steps when responding:
            1️⃣ **Fix Formatting**: Ensure proper headings, spacing, and bullet points.  
            2️⃣ **Enhance Content**: Replace weak wording with strong action verbs.  
            3️⃣ **Ensure ATS Compatibility**: Avoid tables, graphics, and unnecessary formatting.  
            4️⃣ **Provide Clear Suggestions**: Give direct, concise feedback on how to improve each section.  
            ❌ If a user asks for something **unrelated to resumes**, politely remind them that you **only handle resumes**.
            """
        },
        {
            "role": "user",
            "content": f"Here is my resume:\n\n{resume_text}"
        }
    ]

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        temperature=0.62,
        messages=messages,  
        max_completion_tokens=1024,
        top_p=0.9,
        stream=False,  
        stop=None,
    )

    return completion.choices[0].message.content


CUSTOM_CSS = """
<style>
    body { background-color: #1E1E1E; font-family: Arial, sans-serif; }
    .chat-container { display: flex; flex-direction: column; height: 100vh; justify-content: space-between; }
    .chat-title { font-family: "Marker Felt", fantasy, sans-serif;font-size: 24px; color: white; padding: 10px; display: flex; align-items: center; }
    .chat-title img { margin-right: 10px; }
    .chatbox { background-color: #333; height: 450px; border-radius: 10px; padding: 10px; overflow-y: auto; color: white; }
    .input-area { display: flex; align-items: center; padding: 10px; }
    .input-box { flex-grow: 1; border-radius: 8px; padding: 12px; width: 100%; }
    .send-btn { 
        background-color: #007BFF;  
        color: white;  
        padding: 8px 10px;  
        border-radius: 6px;  
        width: 80px;  
        height: 35px;  
        border: none;  
        cursor: pointer;
        transition: 0.2s ease-in-out;
    }
    .send-btn:hover {
        background-color: #0056b3;  
    }
    .action-buttons button { font-size: 12px; padding: 6px 8px; width: 80px; height: 30px;}
</style>
"""

def update_language(selected_lang):
    """Fast updates to UI elements when language changes."""
    lang_code = LANGUAGES.get(selected_lang, "en")
    translations = TRANSLATIONS.get(lang_code, TRANSLATIONS["en"])
    return (
        f'<div class="chat-title">{translations["title"]}</div>',  # Preserve the class
        gr.update(placeholder=translations["placeholder"]),  # Update textbox placeholder
        translations["clear"],  # Update clear button text
        translations["enter"],  # Update enter button text
    )


with gr.Blocks(theme=gr.themes.Ocean(primary_hue="blue", secondary_hue="sky"), css=CUSTOM_CSS) as demo:
    
    with gr.Row():
        title = gr.HTML("<div class='chat-title'>ResumeGenie</div>")
        with gr.Column():
            # Place the dropdown and clear button in the same row
            with gr.Row():
                lang_dropdown = gr.Dropdown(
                    choices=list(LANGUAGES.keys()),
                    label="Select Language",
                    value="English",
                    scale=1,  # Adjust the scale to control width
                )
                clear_btn = gr.Button("🗑 Clear", variant="secondary")

    chatbox = gr.Chatbot(label="Chat History", height=450)

    with gr.Row():
        user_input = gr.Textbox(
            placeholder="How can we help with your resume?",
            lines=1,
            elem_id="input-box",
            show_label=False,
            scale=5
        )
        send_button = gr.Button("Enter", variant="primary" , elem_id="send-btn")
        voice_input = gr.Audio(
        sources=["microphone"],
        type="filepath",
        label="Voice Recognition Chat",
        format="wav"  
)


    def update_chatbot(user_text, chat_history):
        """Handles user input and updates chat history dynamically."""
        
        if not user_text.strip():
            return "", chat_history  # Prevent empty messages

        response = chat_with_bot_stream(user_text)
        chat_history.append((user_text, response))  # Append message history correctly

        return "", chat_history
    
    import logging

    logging.basicConfig(level=logging.INFO)
    
    def process_voice_input(audio_file, chat_history):
        """Processes voice input and updates chat history."""
        if audio_file:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            try:
                logging.info(f"Processing audio file: {audio_file}")
                with sr.AudioFile(audio_file) as source:
                    audio = recognizer.record(source)
                    user_text = recognizer.recognize_google(audio)  # Convert speech to text
                    logging.info(f"Recognized text: {user_text}")
                    return update_chatbot(user_text, chat_history)  # Update chatbot with recognized text
            except sr.UnknownValueError:
                logging.error("Could not understand audio")
                return "Could not understand audio", chat_history
            except sr.RequestError as e:
                logging.error(f"Speech recognition service failed: {e}")
                return f"Speech recognition service failed: {str(e)}", chat_history
            except Exception as e:
                logging.error(f"An error occurred: {e}")
                return f"An error occurred: {str(e)}", chat_history
        logging.warning("No audio file provided")
        return "", chat_history  # Return empty if no audio file
        
    lang_dropdown.change(
        fn=update_language,
        inputs=[lang_dropdown],
        outputs=[title, user_input, clear_btn, send_button],  # Removed voice_input
    )

    send_button.click(
        fn=update_chatbot,
        inputs=[user_input, chatbox],
        outputs=[user_input, chatbox],
        queue=True
    )

    voice_input.stop_recording(
        fn=process_voice_input,
        inputs=[voice_input, chatbox],
        outputs=[user_input, chatbox],
        queue=True
    )

    clear_btn.click(
        lambda: [],
        inputs=[],
        outputs=[chatbox],
        queue=False
    )

demo.queue(api_open=False).launch()