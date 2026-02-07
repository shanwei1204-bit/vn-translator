import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import base64
import json

# --- 1. 基礎設定 ---
st.set_page_config(page_title="中越精準翻譯 (Google模式)", layout="wide")

# 連接 OpenAI
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("找不到 API Key，請檢查 Secrets 設定。")
    st.stop()

# --- 2. 初始化記憶體 (確保按鈕按下後內容不消失) ---
if "draft_text" not in st.session_state:
    st.session_state.draft_text = ""  # 暫存錄到的文字
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None # 判斷是不是新錄音
if "translation_result" not in st.session_state:
    st.session_state.translation_result = None # 最終翻譯結果

st.title("🇻🇳 中越翻譯助手 (確認模式) 🇹🇼")
st.markdown("---")

# --- 3. 側邊欄：輸入區 ---
with st.sidebar:
    st.header("1️⃣ 輸入區")
    
    st.subheader("🎤 語音輸入 (Google 模式)")
    st.write("點擊錄音 -> 停止 -> 檢查文字 -> 確認翻譯")
    # 錄音元件
    audio_input = mic_recorder(start_prompt="🔴 錄音", stop_prompt="⏹️ 停止", key='recorder')
    
    st.markdown("---")
    st.subheader("📷 截圖/照片")
    image_input = st.file_uploader("上傳 Line 截圖", type=["jpg", "jpeg", "png"])
    
    st.markdown("---")
    st.subheader("✍️ 文字輸入")
    text_input = st.text_area("直接打字...", height=100)
    
    # 手動送出文字按鈕
    if st.button("送出文字"):
        if text_input:
            st.session_state.draft_text = text_input
            st.session_state.translation_result = None # 清空舊翻譯

# --- 4. 核心邏輯區 ---

# [邏輯 A] 處理剛錄好的聲音 -> 轉成文字 (但不翻譯)
if audio_input is not None and audio_input != st.session_state.last_audio:
    with st.spinner("👂 正在辨識語音..."):
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=("temp.wav", audio_input['bytes']), 
            response_format="text"
        )
        st.session_state.draft_text = transcript # 存入草稿區
        st.session_state.last_audio = audio_input # 更新錄音狀態
        st.session_state.translation_result = None # 清空舊翻譯，準備新一輪

# [邏輯 B] 處理圖片 -> 轉成描述 (但不翻譯)
if image_input:
    # 圖片比較特殊，通常直接翻譯，但這裡我們為了統一，先存狀態
    # 這裡簡化處理：如果有圖，直接進入翻譯流程
    pass 

# --- 5. 主畫面：確認與結果 ---

# 階段一：顯示「我聽到的內容」(讓用戶確認)
if st.session_state.draft_text and not st.session_state.translation_result:
    st.info("👂 我聽到/看到了：")
    
    # 顯示大字體讓你看得清楚
    st.markdown(f"### `{st.session_state.draft_text}`")
    
    col_confirm, col_clear = st.columns([1, 1])
    
    # 確認翻譯按鈕
    with col_confirm:
        if st.button("✅ 沒錯，翻譯！", type="primary"):
            with st.spinner("
