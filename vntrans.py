import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# --- 1. 介面設定 ---
st.set_page_config(layout="wide", page_title="中越對講機")
st.title("🗣️ 中越對講機 (純翻譯模式)")

# 載入金鑰
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# --- 2. 核心功能：翻譯與語音 ---
def translate_and_speak(text):
    # AI 翻譯邏輯：自動偵測語言
    prompt = f"你是一個專業翻譯機。如果輸入是中文，請翻成道地北越口音越南文；如果輸入是越南文，請翻成流暢中文。稱謂使用：1982年男(Anh)，1998年女(Em)。只需輸出翻譯結果，不要有任何解釋。"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text}]
    )
    result = response.choices[0].message.content
    
    # 顯示翻譯結果
    st.subheader(f"👉 {result}")
    
    # 生成語音 (如果是翻譯成越文，就唸越文)
    voice_res = client.audio.speech.create(
        model="tts-1",
        voice="nova", 
        input=result
    )
    st.audio(voice_res.content, format="audio/mp3", autoplay=True)

# --- 3. 畫面佈局 ---
input_text = st.text_input("請輸入文字（中/越皆可）：", placeholder="在此輸入...")

if st.button("🔊 翻譯並發聲"):
    if input_text:
        translate_and_speak(input_text)
    else:
        st.warning("請先輸入文字")
