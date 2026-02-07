import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder

# 1. 版面設定 (寬螢幕模式)
st.set_page_config(page_title="中越翻譯", layout="wide")

# 連接 OpenAI
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("請設定 Secrets 中的 API Key")
    st.stop()

# 2. 狀態變數 (用來記憶文字)
if "src_text" not in st.session_state:
    st.session_state.src_text = ""
if "res_text" not in st.session_state:
    st.session_state.res_text = ""
if "audio_data" not in st.session_state:
    st.session_state.audio_data = None
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

st.title("🇻🇳 中越翻譯 (Google 介面)")

# 3. 畫面佈局：左右兩欄
col1, col2 = st.columns(2)

# === 左邊：輸入與錄音 ===
with col1:
    st.subheader("輸入 (中文/越文)")
    
    # 錄音按鈕
    audio = mic_recorder(start_prompt="🎤 錄音", stop_prompt="⏹ 停止", key='rec')
    
    # 處理錄音 (如果有新錄音，轉成文字)
    if audio and audio != st.session_state.last_audio:
        with st.spinner("辨識中..."):
            res = client.audio.transcriptions.create(
                model="whisper-1", 
                file=("temp.wav", audio['bytes']), 
                response_format="text"
            )
            st.session_state.src_text = res
            st.session_state.last_audio = audio
            st.rerun()

    # 文字框 (顯示錄音結果，也可手動改)
    user_input = st.text_area("內容：", value=st.session_state.src_text, height=200)
    
    # 如果手動改了字，更新記憶
    if user_input != st.session_state.src_text:
        st.session_state.src_text = user_input

    # 翻譯按鈕
    if st.button("🚀 翻譯 (Translate)", type="primary", use_container_width=True):
        if st.session_state.src_text:
            with st.spinner("翻譯中..."):
                # 呼叫翻譯
                sys = "你是中越翻譯。中文翻越文，越文翻繁體中文。只回傳翻譯結果。"
                resp = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": sys},
                        {"role": "user", "content": st.session_state.src_text}
                    ]
                )
                trans_txt = resp.choices[0].message.content
