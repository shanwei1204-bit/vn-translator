import streamlit as st
from openai import OpenAI
import pyttsx3
import speech_recognition as sr

# --- 初始化 ---
st.set_page_config(layout="wide")
st.title("🎤 中⇄越語音翻譯助手（升級版）")

# --- API Key ---
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("API Key Error")
    st.stop()

# --- 聲音引擎 ---
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# --- 語音辨識 ---
recognizer = sr.Recognizer()
mic = sr.Microphone()

st.write("🔊 點按下方開始錄音，系統會自動偵測中文/越南文並翻譯")

if st.button("開始錄音"):
    with mic as source:
        st.info("請說話...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            # 先用 Google 語音辨識 (語言自動)
            text = recognizer.recognize_google(audio, language="zh-TW")
            st.success(f"你說: {text}")
        except:
            st.error("語音辨識失敗")
            text = ""

        if text:
            # --- 呼叫 OpenAI 翻譯 + 回覆建議 ---
            system_prompt = """
            你是母語等級中越翻譯助手+約會助手。
            中文翻越南文，越南文翻中文。
            翻譯自然口語、簡短、可愛曖昧語氣。
            提供2~3個回覆建議。
            """
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role":"system", "content": system_prompt},
                    {"role":"user", "content": text}
                ]
            )

            result = response.choices[0].message.content
            st.markdown(f"**翻譯 & 回覆建議:**\n{result}")
            engine.say(result)
            engine.runAndWait()
