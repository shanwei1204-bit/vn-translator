import streamlit as st
from openai import OpenAI

# 1. 頁面設定
st.set_page_config(page_title="精準字幕生成", layout="centered")

# 連接 OpenAI
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("請檢查 Secrets 中的 API Key 設定")
    st.stop()

st.title("🎬 MP3 轉 繁體中文 SRT 字幕 (修正版)")
st.info("此版本修復了字幕重複跳針的問題，並加入 GPT-4o 進行繁體校正。")

# 2. 上傳檔案
uploaded_file = st.file_uploader("請上傳音檔 (MP3/M4A/WAV, 25MB以內)", type=["mp3", "m4a", "wav"])

# 3. 執行按鈕
if uploaded_file:
    if st.button("🚀 開始製作字幕", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # --- 第一階段：Whisper 聽寫 (抓取時間軸與文字) ---
            status_text.text("1/2 正在聽寫音檔 (Whisper)...")
            progress_bar.progress(30)
            
            # 這裡把 prompt 縮到最短，避免 AI 發瘋重複指令
            # temperature=0 讓它不要隨意發揮
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=uploaded_file, 
                response_format="srt", 
                prompt="繁體中文", 
                temperature=0
            )
            
            # --- 第二階段：GPT-4o 強制校正 (轉繁體 + 修正錯誤) ---
            status_text.text("2/2 正在進行繁體校正與格式檢查 (GPT-4o)...")
            progress_bar.progress(70)

            # 將剛才生成的 SRT 丟給 GPT-4o 修整
            correction_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": """
                        你是一個專業的字幕編輯。你的任務是將使用者提供的 SRT 字幕內容轉換為「臺灣繁體中文」。
                        規則：
                        1. 絕對不要修改時間軸 (00:00:xx,xxx --> ...)。
                        2. 只翻譯或修改文字部分為通順的繁體中文。
                        3. 如果原本就是繁體，請保留或潤飾。
                        4. 不要輸出任何開場白或結尾，只輸出 SRT 內容。
                        """
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
            st.warning("如果檔案大於 25MB，請先壓縮音檔再上傳。")
