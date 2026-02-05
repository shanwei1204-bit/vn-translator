import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import base64

# 設定 OpenAI Client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="中越實戰翻譯機", layout="centered")
st.title("🇻🇳 中越雙向對話助手 (全能版)")

# --- 功能區 1: 錄音 ---
audio = mic_recorder(start_prompt="🎤 點擊錄音", stop_prompt="⏹️ 停止", key='recorder')

# --- 功能區 2: 圖片翻譯 ---
st.write("---")
uploaded_file = st.file_uploader("📷 上傳 Line 截圖或照片", type=["jpg", "jpeg", "png"])

# --- 功能區 3: 文字貼上 ---
user_text = st.text_input("💬 貼上 Line 文字：")

# 邏輯處理
input_image = None
if uploaded_file:
    # 圖片轉為 Base64 格式給 AI 看
    bytes_data = uploaded_file.read()
    input_image = base64.b64encode(bytes_data).decode('utf-8')
    st.image(uploaded_file, caption="已讀取截圖", use_container_width=True)

# 執行翻譯
if audio or user_text or uploaded_file:
    with st.spinner("AI 正在解析內容..."):
        try:
            messages = [
                {
                    "role": "system", 
                    "content": "你是一位專業翻譯。現在是老公(Anh)與老婆(Em)的對話。1.如果是圖片或越文，請翻成繁體中文並解釋意涵。2.如果是中文，請翻成道地越文(用Anh/Em稱呼)。3.輸出要簡潔、自然。"
                }
            ]
            
            # 判斷輸入類型
            user_content = []
            
            if user_text:
                user_content.append({"type": "text", "text": user_text})
            
            if audio:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", file=("temp.wav", audio['bytes']), response_format="text"
                )
                st.info(f"🎤 識別語音：{transcript}")
                user_content.append({"type": "text", "text": transcript})
            
            if input_image:
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{input_image}"}
                })

            messages.append({"role": "user", "content": user_content})

            # 呼叫 GPT-4o
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=500,
            )
            
            result = response.choices[0].message.content
            st.success(f"✨ 翻譯結果：\n{result}")
            
            # 自動生成越文語音 (如果是中文輸入的話)
            if not input_image and not any('\u4e00' <= char <= '\u9fff' for char in result):
                tts = client.audio.speech.create(model="tts-1", voice="alloy", input=result)
                st.audio(tts.content)
                
        except Exception as e:
            st.error(f"發生錯誤：{e}")

st.divider()
st.caption("這 5 美金花在這裡最值得：不僅能聽、能說、現在還能看了！")
