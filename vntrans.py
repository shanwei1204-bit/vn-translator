import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import base64
import json

# 1. 設定頁面
st.set_page_config(page_title="中越精準翻譯+語音", layout="wide")

# 2. 連接 OpenAI
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("找不到 API Key，請檢查 Secrets 設定。")
    st.stop()

# 3. 初始化 Session State (用來記住翻譯結果，不會因為按按鈕就消失)
if "history" not in st.session_state:
    st.session_state.history = None

st.title("🇻🇳 中越翻譯 & 語音朗讀助手 🇹🇼")
st.markdown("---")

# --- 左側邊欄：輸入區 ---
with st.sidebar:
    st.header("1️⃣ 輸入內容")
    
    # 方式 A: 錄音
    st.subheader("🎤 語音輸入")
    audio_input = mic_recorder(start_prompt="錄音 (點我)", stop_prompt="停止 (點我)", key='recorder')
    
    # 方式 B: 截圖
    st.subheader("📷 截圖/照片")
    image_input = st.file_uploader("上傳 Line 對話截圖", type=["jpg", "jpeg", "png"])
    
    # 方式 C: 文字
    st.subheader("✍️ 文字輸入")
    text_input = st.text_area("輸入要翻譯的文字...", height=100)

    # 執行按鈕
    if st.button("🚀 開始翻譯", type="primary"):
        st.session_state.processing = True

# --- 主邏輯區 ---
if st.session_state.get("processing"):
    with st.spinner("正在分析語意並生成語音..."):
        try:
            # 1. 整理輸入內容
            messages = [
                {"role": "system", "content": """
                你是一個專業的中越口譯員。
                任務：接收使用者的圖片、語音或文字，並進行精準翻譯。
                
                【輸出格式要求】：
                請務必只回傳一個 JSON 格式，
