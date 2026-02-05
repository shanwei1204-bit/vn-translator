import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import base64

# 設定 OpenAI Client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="中越全能助手", layout="centered")

# 使用分頁標籤，讓介面乾淨
tab1, tab2 = st.tabs(["💬 中越翻譯 (語音/截圖)", "🎬 影片轉繁體字幕"])

# --- 第一頁：原本的翻譯功能 ---
with tab1:
    st.header("中越對話助手")
    audio = mic_recorder(start_prompt="🎤 點擊錄音", stop_prompt="⏹️ 停止", key='recorder')
    uploaded_image = st.file_uploader("📷 上傳截圖/照片", type=["jpg", "jpeg", "png"])
    user_text = st.text_input("💬 貼上文字：")

    if audio or user_text or uploaded_image:
        with st.spinner("翻譯中..."):
            try:
                messages = [{"role": "system", "content": "你是一位專業翻譯。現在是老公(Anh)與老婆(Em)的對話。1.如果是圖片或越文，請翻成繁體中文。2.如果是中文，請翻成越文(用Anh/Em稱呼)。"}]
                user_content = []
                if user_text: user_content.append({"type": "text", "text": user_text})
                if audio:
                    transcript = client.audio.transcriptions.create(model="whisper-1", file=("temp.wav", audio['bytes']), response_format="text")
                    user_content.append({"type": "text", "text": transcript})
                if uploaded_image:
                    img_b64 = base64.b64encode(uploaded_image.read()).decode('utf-8')
                    user_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}})
                
                messages.append({"role": "user", "content": user_content})
                response = client.chat.completions.create(model="gpt-4o", messages=messages)
                st.success(response.choices[0].message.content)
            except Exception as e:
                st.error(f"錯誤：{e}")

# --- 第二頁：新增加的影片字幕功能 ---
with tab2:
    st.header("影片自動字幕 (繁體)")
    st.write("將中文影片上傳，直接下載 .srt 字幕檔。")
    video_file = st.file_uploader("🎥 上傳影片或音檔", type=["mp4", "m4a", "mp3", "wav"], key="video")
    
    if video_file:
        if st.button("🚀 開始製作繁體字幕"):
            with st.spinner("OpenAI 雲端製作中，這不會卡住你的電腦..."):
                try:
                    # 使用 prompt 強迫輸出繁體中文
                    srt_content = client.audio.transcriptions.create(
                        model="whisper-1", 
                        file=video_file, 
                        response_format="srt",
                        prompt="這是一個繁體中文的影片，請確保輸出為標準繁體中文，不要使用簡體字。"
                    )
                    st.success("字幕製作成功！")
                    st.text_area("預覽內容", srt_content, height=200)
                    st.download_button("💾 下載繁體 .srt 檔", srt_content, file_name="subtitle.srt")
                except Exception as e:
                    st.error(f"製作失敗：{e}")
