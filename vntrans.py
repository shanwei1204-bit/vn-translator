import streamlit as st
from openai import OpenAI

# 1. 頁面設定
st.set_page_config(page_title="精準字幕生成 (修正版)", layout="centered")

# 連接 OpenAI
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("請檢查 Secrets 中的 API Key 設定")
    st.stop()

st.title("🎬 MP3 轉 繁體中文 SRT 字幕 (最終修正)")
st.warning("此版本修正了「鬼打牆」重複語句的問題，並確保輸出為繁體中文。")

# 2. 上傳檔案
uploaded_file = st.file_uploader("請上傳音檔 (MP3/M4A/WAV, 25MB以內)", type=["mp3", "m4a", "wav"])

# 3. 執行按鈕
if uploaded_file:
    if st.button("🚀 開始製作字幕", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # --- 第一階段：Whisper 聽寫 ---
            status_text.text("1/2 正在聽寫音檔 (Whisper)...")
            progress_bar.progress(20)
            
            # 【關鍵修正】：Prompt 不能寫指令，要寫一段「自然的繁體中文開頭」
            # 這樣 Whisper 就會模仿這個風格繼續寫下去，而不會重複這句話
            safe_prompt = "大家好，這是接下來的影片內容對話。"
            
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=uploaded_file, 
                response_format="srt", 
                prompt=safe_prompt, 
                temperature=0.2 
            )
            
            # --- 第二階段：GPT-4o 強制校正 ---
            status_text.text("2/2 正在進行繁體校正 (GPT-4o)...")
            progress_bar.progress(60)

            # 將生成的 SRT 丟給 GPT-4o 檢查，確保不是簡體，並且修復可能的錯誤
            correction_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "你是一個字幕編輯。請將使用者的 SRT 字幕轉換為標準「台灣繁體中文」。注意：絕對不要更改時間軸，只修正錯字或簡體字。"
                    },
                    {"role": "user", "content": transcript}
                ]
            )
            
            final_srt = correction_response.choices[0].message.content
            
            # 完成
            progress_bar.progress(100)
            status_text.success("🎉 字幕製作完成！")
            
            # 4. 顯示與下載
            st.text_area("字幕預覽", final_srt, height=300)
            
            st.download_button(
                label="💾 下載繁體 .srt 字幕檔",
                data=final_srt,
                file_name="traditional_subtitle.srt",
                mime="text/plain"
            )
            
        except Exception as e:
            st.error(f"發生錯誤：{e}")
            st.info("常見原因：檔案超過 25MB (OpenAI 限制)。請先壓縮音檔。")
