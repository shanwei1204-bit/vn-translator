import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# --- 1. 初始化與金鑰設定 ---
st.set_page_config(layout="wide", page_title="中越翻譯助手")
st.title("🎤 中⇄越語音翻譯助手（OpenAI 高品質版）")

# 先嘗試讀取本地 .env，如果沒有則讀取 Streamlit Secrets
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("找不到 API Key！請在 .env 檔案或 Streamlit Secrets 中設定。")
    st.stop()

client = OpenAI(api_key=api_key)

# --- 2. 語音生成函數 (取代 pyttsx3) ---
def play_voice(text):
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="shimmer", # 推薦女生聲音：shimmer 或 nova
            input=text
        )
        st.audio(response.content, format="audio/mp3")
    except Exception as e:
        st.error(f"語音生成出錯: {e}")

# --- 3. 介面設計 ---
st.write("💡 請在下方輸入文字，系統會自動翻譯並提供回覆建議。")

# 網頁版目前建議使用文字輸入，若要語音輸入需額外安裝 streamlit-mic-recorder
input_text = st.text_input("輸入你想說的話（中文或越文）：", placeholder="例如：妳今天好嗎？")

if st.button("開始翻譯"):
    if input_text:
        with st.spinner("翻譯中..."):
            system_prompt = """
            你是母語等級中越翻譯助手+約會助手。
            1. 中文翻越南文，越南文翻中文。
            2. 翻譯要自然口語、簡短、帶點曖昧語氣。
            3. 提供 2~3 個道地的回覆建議。
            4. 嚴格遵守稱謂：1982年男(Anh), 1998年女(Em)。
            """
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": input_text}
                    ]
                )

                result = response.choices[0].message.content
                st.subheader("✅ 翻譯結果與建議")
                st.markdown(result)
                
                # 自動生成語音播放器
                st.write("---")
                st.write("🔊 語音朗讀：")
                play_voice(result)
                
            except Exception as e:
                st.error(f"API 呼叫失敗: {e}")
    else:
        st.warning("請先輸入文字喔！")
