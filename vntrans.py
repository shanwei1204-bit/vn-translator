import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import base64
import streamlit.components.v1 as components

# 設定 OpenAI Client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="中越語音助手", layout="centered")

# --- 語音朗讀功能的 JavaScript ---
def speak_text(text, lang):
    # lang 傳入 'zh-TW' 或 'vi-VN'
    js_code = f"""
    <script>
    function speak() {{
        var msg = new SpeechSynthesisUtterance('{text.replace("'", "\\'").replace("\\n", " ")}');
        msg.lang = '{lang}';
        window.speechSynthesis.speak(msg);
    }}
    speak();
    </script>
    """
    components.html(js_code, height=0)

st.header("🇻🇳 中越翻譯對照 + 朗讀 🇨🇳")

# --- 輸入區 ---
audio = mic_recorder(start_prompt="🎤 錄製語音", stop_prompt="⏹️ 停止", key='recorder')
uploaded_image = st.file_uploader("📷 上傳老婆的截圖或照片", type=["jpg", "jpeg", "png"])
user_text = st.text_input("💬 貼上要翻譯的文字：")

if audio or user_text or uploaded_image:
    with st.spinner("翻譯中..."):
        try:
            messages = [{
                "role": "system", 
                "content": "你是一位專業翻譯。請將內容翻譯成對應語言（中翻越、越翻繁中）。請格式化輸出：先寫『原文：』，再換行寫『譯文：』。語氣請口語化。"
            }]
            
            user_content = []
            if user_text: user_content.append({"type": "text", "text": user_text})
            if audio:
                transcript = client.audio.transcriptions.create(model="whisper-1", file=("temp.wav", audio['bytes']), response_format="text")
                user_content.append({"type": "text", "text": transcript})
            if uploaded_image:
                img_b64 = base64.b64encode(uploaded_image.read()).decode('utf-8')
                user_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}})

            messages.append({"role": "user", "content": user_content})
            response = client.chat.completions.create(model="gpt-4o", messages=messages)
            full_result = response.choices[0].message.content
            
            # 拆分原文與譯文 (簡單處理)
            parts = full_result.split("譯文：")
            original = parts[0].replace("原文：", "").strip()
            translated = parts[1].strip() if len(parts) > 1 else ""

            # --- 顯示與朗讀區 ---
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📄 原文")
                st.info(original)
                if st.button("🔊 讀原文"):
                    # 簡單判斷語言 (越文通常有特殊符號)
                    lang = 'vi-VN' if any(c in original for c in 'àáảãạăằắẳẵặâầấẩẫậ') else 'zh-TW'
                    speak_text(original, lang)
            
            with col2:
                st.subheader("🎯 譯文")
                st.success(translated)
                if st.button("🔊 讀譯文"):
                    lang = 'zh-TW' if any(c in original for c in 'àáảãạăằắẳẵặâầấẩẫậ') else 'vi-VN'
                    speak_text(translated, lang)
            
        except Exception as e:
            st.error(f"發生錯誤：{e}")
