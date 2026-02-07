import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder

# 1. 設定頁面
st.set_page_config(page_title="中越翻譯", layout="wide")

# 2. 連接 OpenAI (如果沒填 Key 會提示，不會報錯)
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.warning("請在 Secrets 設定 OpenAI API Key")
    st.stop()

# 3. 初始化 (確保變數存在)
if "step" not in st.session_state:
    st.session_state.step = 1
if "draft" not in st.session_state:
    st.session_state.draft = ""
if "result" not in st.session_state:
    st.session_state.result = {}

st.title("🇻🇳 中越翻譯 (Google模式)")

# === 第一步：錄音或輸入 ===
if st.session_state.step == 1:
    st.header("1. 請錄音或輸入")
    
    # 錄音區
    audio = mic_recorder(start_prompt="🔴 錄音 (點我)", stop_prompt="⏹️ 停止 (點我)", key='recorder')
    
    # 文字區
    text_input = st.text_area("或直接打字...")
    
    # 邏輯：如果有錄音，就轉文字
    if audio:
        with st.spinner("辨識中..."):
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=("temp.wav", audio['bytes']), 
                response_format="text"
            )
            st.session_state.draft = transcript
            st.session_state.step = 2
            st.rerun()

    # 邏輯：如果有打字，就送出
    if st.button("送出文字"):
        if text_input:
            st.session_state.draft = text_input
            st.session_state.step = 2
            st.rerun()

# === 第二步：確認內容 ===
elif st.session_state.step == 2:
    st.header("2. 請確認內容")
    
    # 顯示剛剛聽到/寫的字
    st.info(st.session_state.draft)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ 沒錯，翻譯"):
            with st.spinner("翻譯中..."):
                # 簡單的翻譯指令，不使用複雜引號
                prompt = "你是一個中越翻譯。請只回傳翻譯後的文字。如果是中文翻越文，如果是越文翻繁體中文。"
                
                # 呼叫 GPT-4o
                resp = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role":"system", "content": prompt},
                        {"role":"user", "content": st.session_state.draft}
                    ]
                )
                translation_text = resp.choices[0].message.content
                
                # 呼叫 TTS 生成語音
                tts = client.audio.speech.create(
                    model="tts-1", 
                    voice="alloy", 
                    input=translation_text
                )
                
                # 存結果
                st.session_state.result = {
                    "text": translation_text,
                    "audio": tts.content
                }
                st.session_state.step = 3
                st.rerun()
                
    with col2:
        if st.button("❌ 講錯了，重來"):
            st.session_state.step = 1
            st.session_state.draft = ""
            st.rerun()

# === 第三步：顯示結果 ===
elif st.session_state.step == 3:
    st.header("3. 翻譯結果")
    
    # 顯示翻譯文字
    st.success(st.session_state.result["text"])
    
    # 播放語音
    st.audio(st.session_state.result["audio"], format="audio/mp3")
    
    st.markdown("---")
    if st.button("🔄 翻譯下一句"):
        st.session_state.step = 1
        st.session_state.draft = ""
        st.session_state.result = {}
        st.rerun()
