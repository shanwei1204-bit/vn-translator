import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder

# --- 1. 介面設定 (像 Google 一樣寬螢幕) ---
st.set_page_config(page_title="中越翻譯", layout="wide")

# 連接 OpenAI
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("請設定 Secrets 中的 API Key")
    st.stop()

# --- 2. 狀態管理 (記住你輸入的字) ---
if "source_text" not in st.session_state:
    st.session_state.source_text = ""
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "audio_data" not in st.session_state:
    st.session_state.audio_data = None

# 標題
st.markdown("## 🇻🇳 雙向中越翻譯 (Google 風格)")

# --- 3. 畫面佈局 (左右兩欄) ---
col1, col2 = st.columns(2)

# ====== 左邊：輸入區 (來源) ======
with col1:
    st.info("輸入內容 (中文 / 越文)")
    
    # 方式 A: 錄音按鈕
    c_rec, c_info = st.columns([1, 3])
    with c_rec:
        audio_input = mic_recorder(start_prompt="🎤 錄音", stop_prompt="⏹️ 停止", key='recorder')
    with c_info:
        st.caption("點擊錄音，講完按停止。")

    # 處理錄音 (如果有錄音，就轉成文字填入框框)
    if audio_input:
        # 簡單判斷是否為新錄音，避免重複執行
        if "last_audio_id" not in st.session_state or st.session_state.last_audio_id != audio_input['id']:
            with st.spinner("辨識語音中..."):
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=("temp.wav", audio_input['bytes']), 
                    response_format="text"
                )
                st.session_state.source_text = transcript
                st.session_state.last_audio_id = audio_input['id']
                st.rerun()

    # 方式 B: 文字框 (可以修改錄音結果，或是直接打字)
    user_input = st.text_area("在此輸入文字...", value=st.session_state.source_text, height=200)
    
    # 如果使用者手動改了文字，更新狀態
    if user_input != st.session_state.source_text:
        st.session_state.source_text = user_input

    # === 中間動作：翻譯按鈕 ===
    if st.button("🚀 翻譯 (Translate)", type="primary", use_container_width=True):
        if st.session_state.source_text:
            with st.spinner("正在翻譯..."):
                # 1. 呼叫 GPT-4o 翻譯
                sys_msg = "你是一個中越翻譯。請直接翻譯內容。如果是中文翻越文，如果是越文翻繁體
