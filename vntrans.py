import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder

# 安全讀取金鑰 (不要改這行，等等要在雲端後台設定)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="中越 AI 即時翻譯助手", page_icon="🇻🇳")
st.title("🇻🇳 中越 AI 即時翻譯助手")

# 錄音組件
audio = mic_recorder(start_prompt="按住說話", stop_prompt="停止錄音", key='recorder')

if audio:
    # 1. 語音轉文字 (Whisper)
    with st.spinner("辨識中..."):
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=("temp.wav", audio['bytes']),
            response_format="text"
        )
    st.info(f"你說的是：{transcript}")

    # 2. 高準度 AI 翻譯 (GPT-4o)
    with st.spinner("AI 翻譯中..."):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是一位精通中文與越文的翻譯專家。請將中文翻譯成自然道地的越文。考慮人稱代詞並保持口語化。"},
                {"role": "user", "content": transcript}
            ]
        )
        translated_text = response.choices[0].message.content
    
    st.success(f"越文翻譯：{translated_text}")

    # 3. 語音合成 (TTS)
    with st.spinner("合成語音..."):
        tts_response = client.audio.speech.create(
            model="tts-1", voice="alloy", input=translated_text
        )
        st.audio(tts_response.content)