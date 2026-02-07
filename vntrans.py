import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import json

# 1. 基礎設定
st.set_page_config(page_title="中越翻譯助手", layout="wide")

# 連接 OpenAI (如果沒設定好會跳錯)
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("請檢查 Secrets 中的 API Key 設定")
    st.stop()

# 2. 初始化狀態 (確保按鈕按下後不會重置)
if "draft" not in st.session_state:
    st.session_state.draft = ""
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None
if "result" not in st.session_state:
    st.session_state.result = None

st.title("🇻🇳 中越語音翻譯 (確認模式)")

# 3. 側邊欄：輸入區
with st.sidebar:
    st.header("輸入區")
    
    # 錄音元件
    audio = mic_recorder(start_prompt="🔴 錄音", stop_prompt="⏹️ 停止", key='recorder')
    
    # 文字輸入
    text_in = st.text_area("或直接輸入文字...")
    if st.button("送出文字"):
        st.session_state.draft = text_in
        st.session_state.result = None

# 4. 邏輯 A：處理錄音 (轉文字 -> 存入草稿)
if audio is not None and audio != st.session_state.last_audio:
    with st.spinner("正在辨識語音..."):
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=("temp.wav", audio['bytes']), 
            response_format="text"
        )
        st.session_state.draft = transcript
        st.session_state.last_audio = audio
        st.session_state.result = None

# 5. 邏輯 B：顯示確認畫面 (還沒翻譯)
if st.session_state.draft and not st.session_state.result:
    st.info("👂 我聽到/看到了：")
    st.markdown(f"### {st.session_state.draft}")
    
    col1, col2 = st.columns(2)
    with col1:
        # 按下這個才會扣錢翻譯
        if st.button("✅ 確認翻譯", type="primary"):
            with st.spinner("翻譯中..."):
                # 簡單的 Prompt
                prompt = "你是一個中越口譯員。請回傳JSON格式，包含 original(原文), translated(譯文), lang(語言代碼vi或zh)。"
                
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": prompt},
                            {"role": "user", "content": st.session_state.draft}
                        ],
                        response_format={"type": "json_object"}
                    )
                    data = json.loads(response.choices[0].message.content)
                    
                    # 決定語音
                    if data["lang"] == "vi":
                        v1, v2 = "alloy", "nova"
                    else:
                        v1, v2 = "nova", "alloy"
                        
                    tts1 = client.audio.speech.create(model="tts-1", voice=v1, input=data["original"])
                    tts2 = client.audio.speech.create(model="tts-1", voice=v2, input=data["translated"])
                    
                    st.session_state.result = {
                        "orig": data["original"],
                        "trans": data["translated"],
                        "aud1": tts1.content,
                        "aud2": tts2.content
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"錯誤：{e}")

    with col2:
        if st.button("❌ 不對，清除"):
            st.session_state.draft = ""
            st.rerun()

# 6. 邏輯 C：顯示結果
if st.session_state.result:
    res = st.session_state.result
    
    if st.button("🔄 翻譯下一句"):
        st.session_state.draft = ""
        st.session_state.result = None
        st.rerun()
        
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.success("原文")
        st.write(res["orig"])
        st.audio(res["aud1"])
    with c2:
        st.error("翻譯")
        st.write(res["trans"])
        st.audio(res["aud2"])
