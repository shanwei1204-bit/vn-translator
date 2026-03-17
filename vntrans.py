import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# --- 1. 頁面精美設定 ---
st.set_page_config(layout="centered", page_title="Anh & Em 專屬翻譯官", page_icon="❤️")
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #ff4b4b; color: white; }
    .stTextInput>div>div>input { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌹 中越愛情翻譯助手 (Pro 版)")
st.caption("專為 1982 Anh 與 1998 河內 Em 設計")

# 讀取金鑰
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("❌ 找不到 API Key，請檢查 Streamlit Secrets 設定！")
    st.stop()

client = OpenAI(api_key=api_key)

# --- 2. 核心邏輯：語音生成 ---
def play_voice(text):
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova", # 溫柔的女聲
            input=text
        )
        st.audio(response.content, format="audio/mp3", autoplay=True)
    except Exception as e:
        st.error(f"語音出錯: {e}")

# --- 3. 介面與功能 ---
input_text = st.text_area("✍️ 請輸入 Em 說的話或你想說的話：", placeholder="例如：Em không cần đâu...", height=100)

if st.button("✨ 開始分析與翻譯"):
    if input_text.strip():
        with st.spinner("正在讀取 Em 的心意..."):
            system_prompt = """
            你是一位精通北越文化、專門處理年齡差戀愛的諮詢專家。
            【背景】使用者是 Anh (1982年)，對象是 Em (1998年河內女性，屬虎)。
            
            【任務】請針對輸入內容進行以下分析：
            1. 【原文翻譯】：翻譯成道地、深情的中文。
            2. 【情緒偵測】：用一句話點破 Em 現在的真實心情（傲嬌、生氣、暗示、撒嬌）。
            3. 【撩妹回覆建議】：
               - 提供 3 個選項：(1)霸氣保護 (2)幽默化解 (3)深情告白。
               - 必須使用道地北越 (Hanoi) 語氣，稱謂嚴格遵守 Anh/Em。
               - 回覆要短小精悍，不要像寫作文。
            """
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": input_text}
                    ],
                    temperature=0.8
                )

                res_content = response.choices[0].message.content
                
                # 顯示結果
                st.success("分析完成！")
                st.markdown("---")
                st.markdown(res_content)
                
                # 自動唸出第一條建議或原文
                st.write("📢 **語音播放中...**")
                play_voice(res_content.split('】')[-1]) # 唸出最後一部分的回覆
                
            except Exception as e:
                st.error(f"連線失敗: {e}")
    else:
        st.warning("請先寫點東西喔，Anh！")

st.markdown("---")
st.info("💡 提示：如果是 Em 傳來的語音，你可以把語音轉文字後貼過來分析。")
