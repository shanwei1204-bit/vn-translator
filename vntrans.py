import streamlit as st
from openai import OpenAI

# 1. 頁面設定
st.set_page_config(page_title="越翻中字幕生成", layout="centered")

# 連接 OpenAI
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("請檢查 Secrets 中的 API Key 設定")
    st.stop()

st.title("🇻🇳 越語 MP3 轉 🇹🇼 繁體字幕")
st.info("採用「先聽寫越文、再翻譯中文」的雙重架構，確保準確度最高。")

# 2. 上傳檔案
uploaded_file = st.file_uploader("請上傳越南語音檔 (MP3/M4A/WAV, 限25MB)", type=["mp3", "m4a", "wav"])

# 3. 執行按鈕
if uploaded_file:
    if st.button("🚀 開始製作繁體字幕", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # --- 第一階段：Whisper 聽寫 (鎖定越南語) ---
            status_text.text("1/2 正在聽寫越南語原文 (Whisper)...")
            progress_bar.progress(30)
            
            # 強制指定 language="vi"，讓它專心聽越南話，不要胡思亂想
            transcript_vi = client.audio.transcriptions.create(
                model="whisper-1", 
                file=uploaded_file, 
                response_format="srt", 
                language="vi",  # 關鍵：指定聽越南語
                temperature=0   # 關鍵：讓它不要亂發揮
            )
            
            # --- 第二階段：GPT-4o 翻譯 (越 -> 繁中) ---
            status_text.text("2/2 正在將越文翻譯成繁體中文 (GPT-4o)...")
            progress_bar.progress(70)

            # 將越文 SRT 丟給 GPT-4o 翻譯
            translation_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": """
