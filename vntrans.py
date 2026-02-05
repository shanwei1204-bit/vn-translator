import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder

# 1. 讀取你在 Streamlit 後台設定的 Secrets 金鑰
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 網頁基本設定
st.set_page_config(page_title="中越即時對話助手", page_icon="🇻🇳")
st.title("🇻🇳 中越雙向溝通助手")
st.write("自動偵測中越語，使用 Anh (哥哥) 與 Em (妹妹) 自然稱謂。")

# 2. 錄音組件 (支援手機 HTTPS 錄音)
audio = mic_recorder(
    start_prompt="按住說話", 
    stop_prompt="停止錄音", 
    key='recorder'
)

if audio:
    with st.spinner("辨識中..."):
        # A. 語音轉文字
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=("temp.wav", audio['bytes']),
            response_format="text"
        )
        st.info(f"🎤 辨識內容：{transcript}")

        # B. GPT-4o 專業對話翻譯
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system", 
                    "content": """你是一位專業的中越雙語對話翻譯官。
                    情境：老公(台灣人)與老婆(越南人)的日常對話。
                    稱謂規則：
                    1. 中翻越：老公自稱 'Anh'，稱呼老婆為 'Em'。
                    2. 越翻中：老婆自稱 'Em'，稱呼老公為 'Anh' (翻成中文時使用'老公'或'你'，視語境而定)。
                    3. 風格：語氣要自然、口語，符合日常生活中哥哥與妹妹的平等的對話感。
                    4. 輸出：只輸出翻譯結果，不要有任何解釋。"""
                },
                {"role": "user", "content": transcript}
            ]
        )
        translated_text = response.choices[0].message.content
        st.success(f"✨ 翻譯結果：{translated_text}")
        
        # C. 語音合成 (TTS)
        tts_response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=translated_text
        )
        st.audio(tts_response.content)

st.divider()
st.caption("使用說明：點擊按鈕錄音後，AI 會自動判斷是誰在說話並翻譯。")
