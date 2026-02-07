import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import base64

# 設定 OpenAI Client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="中越翻譯對照助手", layout="centered")

st.header("🇻🇳 中越雙向翻譯助手 (對照版) 🇨🇳")
st.write("支援語音、截圖、文字，並保留原文供您比照準確度。")

# --- 輸入區 ---
audio = mic_recorder(start_prompt="🎤 錄製語音", stop_prompt="⏹️ 停止", key='recorder')
uploaded_image = st.file_uploader("📷 上傳老婆的截圖或照片", type=["jpg", "jpeg", "png"])
user_text = st.text_input("💬 貼上要翻譯的文字：")

if audio or user_text or uploaded_image:
    with st.spinner("翻譯中..."):
        try:
            # 建立翻譯指令
            messages = [{
                "role": "system", 
                "content": """你是一位專業的中越翻譯顧問。現在是老公(Anh)與老婆(Em)的對話。
                你的任務是：
                1. 判斷輸入語言。如果是中文就翻成越文；如果是越文就翻成繁體中文。
                2. 翻譯語氣要自然、口語化。
                3. 請務必保留『原文』在最上方，然後在下方提供『翻譯結果』，方便用戶比照準不準。"""
            }]
            
            user_content = []
            
            # 處理文字
            if user_text:
                user_content.append({"type": "text", "text": f"請翻譯這段文字：{user_text}"})
            
            # 處理語音 (先轉文字)
            if audio:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=("temp.wav", audio['bytes']), 
                    response_format="text"
                )
                user_content.append({"type": "text", "text": f"這是語音轉錄的原文：{transcript}。請翻譯它。"})
            
            # 處理截圖 (圖片轉文字+翻譯)
            if uploaded_image:
                img_b64 = base64.b64encode(uploaded_image.read()).decode('utf-8')
                user_content.append({
                    "type": "image_url", 
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                })

            messages.append({"role": "user", "content": user_content})
            
            # 呼叫 GPT-4o
            response = client.chat.completions.create(
                model="gpt-4o", 
                messages=messages
            )
            
            # --- 顯示結果區 ---
            st.markdown("---")
            st.subheader("📊 翻譯結果對照")
            st.markdown(response.choices[0].message.content)
            
        except Exception as e:
            st.error(f"發生錯誤：{e}")

st.info("💡 提示：如果您上傳的是老婆的 Line 截圖，AI 會自動辨識上面的越文並翻譯成繁體中文。")
