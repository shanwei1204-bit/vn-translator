import streamlit as st
from openai import OpenAI

# 1. 設定頁面
st.set_page_config(page_title="MP3 轉 繁體字幕", layout="centered")

# 連接 OpenAI
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("請檢查 Secrets 中的 API Key 設定")
    st.stop()

st.title("🎬 MP3 轉 繁體中文 SRT 字幕")
st.write("使用 OpenAI Whisper-1 模型，準確度最高。")

# 2. 上傳檔案
uploaded_file = st.file_uploader("請上傳 MP3 / M4A / WAV 檔案 (限制 25MB 以內)", type=["mp3", "m4a", "wav"])

# 3. 開始轉錄按鈕
if uploaded_file:
    if st.button("🚀 開始製作字幕", type="primary"):
        with st.spinner("OpenAI 正在聽寫並生成字幕中 (請稍候)..."):
            try:
                # 關鍵設定：透過 prompt 強制它輸出繁體中文
                # response_format="srt" 會直接給出字幕格式
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=uploaded_file, 
                    response_format="srt", 
                    prompt="這是一段繁體中文的對話。請使用繁體中文(Traditional Chinese)輸出，不要使用簡體字。"
                )
                
                st.success("🎉 字幕製作完成！")
                
                # 4. 顯示與下載
                st.text_area("字幕預覽", transcript, height=200)
                
                # 下載按鈕
                st.download_button(
                    label="💾 下載 .srt 字幕檔",
                    data=transcript,
                    file_name="subtitle.srt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"發生錯誤：{e}")
                st.info("提示：如果檔案超過 25MB，OpenAI 會拒收。請先壓縮音檔。")
