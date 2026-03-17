import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder

# --- 1. 介面與金鑰設定 ---
st.set_page_config(layout="centered", page_title="中越對講機")
st.title("🗣️ 中越快速對講機")
st.caption("1982 Anh 專用 | 自動偵測模式")

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# --- 2. 核心功能：聰明翻譯 ---
def process_smart_translation(text):
    # 讓 AI 判斷：輸入是中文就給越文，輸入是越文就給中文
    prompt = f"""
    你是一個專業的中越對講機。
    使用者身分：1982年男(Anh)，對象：1998年女(Em)。
    
    規則：
    1. 如果輸入是【中文】，請翻譯成【道地北越口音越南文】，只需輸出翻譯結果。
    2. 如果輸入是【越南文】，請翻譯成【流暢的繁體中文】，只需輸出翻譯結果。
    不要有任何解釋、不要有註解。
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text}]
    )
    result = response.choices[0].message.content.strip()

    # --- 判斷輸出語言來決定是否播放語音 ---
    # 簡單判斷：如果結果包含中文字，就是翻譯給 Anh 看的
    is_to_chinese = any('\u4e00' <= char <= '\u9fff' for char in result)

    if is_to_chinese:
        st.subheader("🇨🇳 中文意思：")
        st.success(result)
        # 翻成中文就不播放聲音，避免吵到你
    else:
        st.subheader("🇻🇳 越南文：")
        st.info(result)
        # 翻成越南文，自動播放聲音給 Em 聽
        voice_res = client.audio.speech.create(
            model="tts-1",
            voice="nova", 
            input=result
        )
        st.audio(voice_res.content, format="audio/mp3", autoplay=True)

# --- 3. 介面佈局 ---
# 語音錄音
st.write("🎤 語音輸入 (按一下開始，再按一下停止)：")
audio_record = mic_recorder(start_prompt="🔴 開始錄音", stop_prompt="⏹️ 停止並翻譯", key='recorder')

if audio_record:
    with st.spinner("辨識中..."):
        with open("temp.wav", "wb") as f:
            f.write(audio_record['bytes'])
        audio_file = open("temp.wav", "rb")
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        st.write(f"📝 辨識內容：{transcript.text}")
        process_smart_translation(transcript.text)

st.write("---")

# 手動輸入
manual_text = st.text_input("或是直接輸入文字（中/越皆可）：")
if st.button("🚀 執行翻譯"):
    if manual_text:
        process_smart_translation(manual_text)
