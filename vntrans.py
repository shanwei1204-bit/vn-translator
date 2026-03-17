import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder

# --- 1. 介面與金鑰設定 ---
st.set_page_config(layout="centered", page_title="中越對講機")
st.markdown("<style>.stButton>button { height: 3em; font-size: 20px; }</style>", unsafe_allow_html=True)

st.title("🗣️ 中越語音對講機")
st.caption("1982 Anh 專用 | 繁體中文介面")

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# --- 2. 核心功能：翻譯與語音 ---
def process_translation(text):
    # 強制要求：翻譯結果 + 逐字註解
    prompt = f"""
    你是一個專業翻譯機。
    請將輸入的內容翻譯成道地北越口音越南文。
    稱謂使用：1982年男(Anh)，1998年女(Em)。
    
    輸出格式要求：
    第一行：純越南文翻譯內容
    第二行：【逐字註解】單字=意思, 單字=意思...
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text}]
    )
    full_res = response.choices[0].message.content.split('\n')
    vn_text = full_res[0].strip()
    annotation = full_res[1].strip() if len(full_res) > 1 else ""

    # 顯示結果
    st.markdown(f"### 🇻🇳 越南文：\n## {vn_text}")
    st.info(f"💡 {annotation}")
    
    # 播放語音
    voice_res = client.audio.speech.create(
        model="tts-1",
        voice="nova", 
        input=vn_text
    )
    st.audio(voice_res.content, format="audio/mp3", autoplay=True)

# --- 3. 語音錄音元件 ---
st.write("點擊下方麥克風圖示開始錄音：")
audio_record = mic_recorder(
    start_prompt="🔴 按下開始錄音",
    stop_prompt="⏹️ 停止並翻譯",
    key='recorder'
)

if audio_record:
    # 將錄音檔傳給 OpenAI Whisper 轉文字
    with st.spinner("辨識語音中..."):
        with open("temp_audio.wav", "wb") as f:
            f.write(audio_record['bytes'])
        
        audio_file = open("temp_audio.wav", "rb")
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        st.write(f"🎤 你說的是：{transcript.text}")
        process_translation(transcript.text)

# --- 4. 手動輸入備用 ---
st.write("---")
manual_text = st.text_input("或是手動輸入中文：")
if st.button("🚀 翻譯手動內容"):
    if manual_text:
        process_translation(manual_text)
