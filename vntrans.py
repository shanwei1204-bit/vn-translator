import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder

# 1. 安全讀取你在 Streamlit Secrets 設定的金鑰
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 設定網頁標題
st.set_page_config(page_title="中越雙向 AI 翻譯助手", page_icon="🇻🇳")
st.title("🇻🇳 中越雙向對話助手")
st.write("點擊下方麥克風，講中文或越文都可以，AI 會自動辨識翻譯。")

# 2. 錄音組件 (支援手機麥克風)
audio = mic_recorder(
    start_prompt="按住說話 (中/越皆可)", 
    stop_prompt="停止錄音", 
    key='recorder'
)

if audio:
    with st.spinner("AI 正在辨識並翻譯中..."):
        # A. 語音轉文字 (Whisper 引擎自動辨識語言)
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=("temp.wav", audio['bytes']),
            response_format="text"
        )
        st.info(f"偵測內容：{transcript}")

        # B. GPT-4o 聰明翻譯邏輯 (判斷中翻越 或 越翻中)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": "你是一位精通中越雙語的專業翻譯。如果輸入是中文，請翻譯成自然道地的越南文；如果輸入是越南文，請翻譯成自然道地的繁體中文。請根據對象適當調整越文人稱，保持口語化，只輸出翻譯結果。"
                },
                {"role": "user", "content": transcript}
            ]
        )
        translated_text = response.choices[0].message.content
        st.success(f"翻譯結果：{translated_text}")
        
        # C. 語音合成 (TTS) - 讓 AI 把翻譯結果唸出來
        tts_response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=translated_text
        )
        st.audio(tts_response.content)

st.divider()
st.caption("提示：請確保手機音量已開啟。如果是越南朋友說話，請將手機靠近對方。")
