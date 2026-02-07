import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import json

# 1. 基礎設定
st.set_page_config(page_title="中越翻譯 (Google模式)", layout="wide")

# 連接 OpenAI
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("找不到 API Key，請檢查 Secrets 設定。")
    st.stop()

# 2. 初始化變數
if "draft_text" not in st.session_state:
    st.session_state.draft_text = ""
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None
if "translation_result" not in st.session_state:
    st.session_state.translation_result = None

st.title("🇻🇳 中越翻譯助手 (確認模式) 🇹🇼")

# 3. 側邊欄輸入
with st.sidebar:
    st.header("輸入區")
    
    st.write("1. 語音輸入")
    audio_input = mic_recorder(start_prompt="🔴 錄音", stop_prompt="⏹️ 停止", key='recorder')
    
    st.write("2. 文字輸入")
    text_input = st.text_area("輸入文字...")
    
    if st.button("送出文字"):
        if text_input:
            st.session_state.draft_text = text_input
            st.session_state.translation_result = None

# 4. 處理語音 (轉文字但不翻譯)
if audio_input is not None and audio_input != st.session_state.last_audio:
    with st.spinner("正在辨識語音..."):
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=("temp.wav", audio_input['bytes']), 
            response_format="text"
        )
        st.session_state.draft_text = transcript
        st.session_state.last_audio = audio_input
        st.session_state.translation_result = None

# 5. 主畫面：確認與翻譯
# 情況 A: 有草稿，還沒翻譯 -> 顯示確認按鈕
if st.session_state.draft_text and not st.session_state.translation_result:
    st.info("請確認您說的話：")
    st.markdown(f"### {st.session_state.draft_text}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ 確認翻譯", type="primary"):
            with st.spinner("翻譯中..."):
                # 準備 Prompt (簡化版，避免格式錯誤)
                sys_msg = "你是一個中越口譯員。請回傳JSON格式，包含 original(原文), translated(譯文), lang(語言代碼vi或zh)。"
                
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": sys_msg},
                            {"role": "user", "content": st.session_state.draft
