import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder

# 設定寬螢幕，像 Google 翻譯一樣
st.set_page_config(layout="wide")

# 連接 OpenAI
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("API Key 設定錯誤")
    st.stop()

# 初始化變數
if "text_in" not in st.session_state:
    st.session_state.text_in = ""
if "text_out" not in st.session_state:
    st.session_state.text_out = ""
if "audio_out" not in st.session_state:
    st.session_state.audio_out = None

st.title("🇻🇳 中越翻譯 (Google 模式)")

# 建立左右兩欄
col1, col2 = st.columns(2)

# === 左邊：輸入區 ===
with col1:
    st.subheader("輸入 (中文 / 越文)")
    
    # 錄音按鈕
    audio = mic_recorder(start_prompt="🔴 錄音", stop_prompt="⏹ 停止", key='rec')
    
    # 如果錄音完成，轉文字
    if audio:
        with st.spinner("辨識中..."):
            res = client.audio.transcriptions.create(
                model="whisper-1", 
                file=("temp.wav", audio['bytes']), 
                response_format="text"
            )
            # 只有當內容不同時才更新，避免迴圈
            if res != st.session_state.text_in:
                st.session_state.text_in = res
                st.rerun()

    # 文字輸入框 (可修改錄音結果)
    user_text = st.text_area("內容", value=st.session_state.text_in, height=200)
    
    # 同步變數
    if user_text != st.session_state.text_in:
        st.session_state.text_in = user_text

    # 翻譯按鈕
    if st.button("🚀 翻譯", type="primary", use_container_width=True):
        if st.session_state.text_in:
            with st.spinner("翻譯中..."):
                # 1. 翻譯
                sys_msg = "你是中越翻譯。中文翻越文，越文翻繁體中文。只回傳結果。"
                resp = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": sys_msg},
                        {"role": "user", "content": st.session_state.text_in}
                    ]
                )
                trans_text = resp.choices[0].message.content
                st.session_state.text_out = trans_text

                # 2. 語音生成
                # 簡單判斷：有中文就當原文是中文，所以目標唸越文(alloy)
                # 否則唸中文(nova)
                is_chinese = False
                for char in st.session_state.text_in:
                    if "\u4e00" <= char <= "\u9fff":
                        is_chinese = True
                        break
                
                if is_chinese:
                    voice = "alloy" # 唸越文
                else:
                    voice = "nova"  # 唸中文

                tts = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=trans_text
                )
                st.session_state.audio_out = tts.content
                st.rerun()

# === 右邊：結果區 ===
with col2:
    st.subheader("翻譯結果")
    
    # 顯示翻譯文字
    st.text_area("結果", value=st.session_state.text_out, height=200)
    
    # 播放語音
    if st.session_state.audio_out:
        st.audio(st.session_state.audio_out, format="audio/mp3")

# 清除按鈕
if st.button("🔄 重置"):
    st.session_state.text_in = ""
    st.session_state.text_out = ""
    st.session_state.audio_out = None
    st.rerun()
