import streamlit as st
from openai import OpenAI

# 1. 頁面設定
st.set_page_config(page_title="SRT 字幕生成 (最終版)", layout="centered")

# 連接 OpenAI
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("請檢查 Secrets 中的 API Key 設定")
    st.stop()

st.title("🎬 MP3 轉 繁體 SRT 字幕 (防迴圈版)")
st.write("採用「先聽寫、後轉繁體」策略，徹底杜絕無限重複問題。")

# 2. 上傳檔案
uploaded_file = st.file_uploader("請上傳音檔 (MP3/M4A/WAV, 限制 25MB 以內)", type=["mp3", "m4a", "wav"])

# 3. 執行按鈕
if uploaded_file:
    if st.button("🚀 開始製作字幕", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # --- 第一階段：Whisper 裸聽 (不加任何 Prompt) ---
            # 這是唯一能防止「無限迴圈」的方法
            status_text.text("1/2 正在聽寫 (Whisper)...")
            progress_bar.progress(30)
            
            transcript_response = client.audio.transcriptions.create(
                model="whisper-1", 
                file=uploaded_file, 
                response_format="srt", # 直接拿 SRT 格式
                language="zh"          # 指定聽中文，但不指定內容，避免干擾
            )
            
            # --- 第二階段：GPT-4o 轉繁體 ---
            status_text.text("2/2 正在轉為繁體中文 (GPT-4o)...")
            progress_bar.progress(70)

            # 將生成的 SRT (可能是簡體) 丟給 GPT-4o 轉繁體
            correction_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": """
                        你是一個字幕轉換工具。任務是將輸入的 SRT 字幕轉為「台灣繁體中文」。
                        嚴格遵守：
                        1. 絕對保留原本的時間軸格式 (00:00:xx,xxx --> ...)。
                        2. 絕對不要刪減行數。
                        3. 只將簡體字轉為繁體，並修正明顯的同音錯字。
                        4. 直接輸出 SRT 內容，不要有任何開場白。
                        """
                    },
                    {"role": "user", "content": transcript_response}
                ],
                temperature=0 # 讓 AI 嚴謹，不要亂發揮
            )
            
            final_srt = correction_response.choices[0].message.content
            
            # 完成
            progress_bar.progress(100)
            status_text.success("🎉 字幕製作完成！")
            
            # 4. 顯示與下載
            st.text_area("字幕結果", final_srt, height=300)
            
            st.download_button(
                label="💾 下載繁體 .srt 字幕檔",
                data=final_srt,
                file_name="video_subtitles.srt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"發生錯誤：{e}")
            st.warning("如果出現 413 錯誤，代表檔案超過 25MB。請先壓縮音檔。")
