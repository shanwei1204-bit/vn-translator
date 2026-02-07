import streamlit as st
from openai import OpenAI
from streamlit_mic_recorder import mic_recorder
import base64
import json

# 1. 設定頁面
st.set_page_config(page_title="中越精準翻譯+語音", layout="wide")

# 2. 連接 OpenAI
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("找不到 API Key，請檢查 Secrets 設定。")
    st.stop()

# 3. 初始化 Session State (確保翻譯結果不會消失)
if "history" not in st.session_state:
    st.session_state.history = None
if "processing" not in st.session_state:
    st.session_state.processing = False

st.title("🇻🇳 中越翻譯 & 語音朗讀助手 🇹🇼")
st.markdown("---")

# --- 左側邊欄：輸入區 ---
with st.sidebar:
    st.header("1️⃣ 輸入內容")
    
    # 方式 A: 錄音
    st.subheader("🎤 語音輸入")
    audio_input = mic_recorder(start_prompt="錄音 (點我)", stop_prompt="停止 (點我)", key='recorder')
    
    # 方式 B: 截圖
    st.subheader("📷 截圖/照片")
    image_input = st.file_uploader("上傳 Line 對話截圖", type=["jpg", "jpeg", "png"])
    
    # 方式 C: 文字
    st.subheader("✍️ 文字輸入")
    text_input = st.text_area("輸入要翻譯的文字...", height=100)

    # 執行按鈕
    if st.button("🚀 開始翻譯", type="primary"):
        st.session_state.processing = True

# --- 主邏輯區 ---
if st.session_state.processing:
    with st.spinner("正在分析語意並生成語音..."):
        try:
            # 1. 整理輸入內容
            # 注意：這裡使用了三個引號，請確保複製完整
            system_prompt = """
            你是一個專業的中越口譯員。
            任務：接收使用者的圖片、語音或文字，並進行精準翻譯。
            
            【輸出格式要求】：
            請務必只回傳一個 JSON 格式，不要有其他廢話。格式如下：
            {
                "original_text": "這裡放識別到的原文内容",
                "translated_text": "這裡放翻譯後的繁體中文(或越文)",
                "source_lang": "vi"
            }
            注意：source_lang 如果是越文填 vi, 中文填 zh。
            """

            messages = [{"role": "system", "content": system_prompt}]
            
            user_content = []
            
            # 處理文字
            if text_input:
                user_content.append({"type": "text", "text": text_input})
            
            # 處理語音 (Whisper 轉文字)
            if audio_input:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=("temp.wav", audio_input['bytes']), 
                    response_format="text"
                )
                user_content.append({"type": "text", "text": f"語音內容：{transcript}"})
            
            # 處理圖片 (GPT-4o 視覺)
            if image_input:
                img_b64 = base64.b64encode(image_input.read()).decode('utf-8')
                user_content.append({
                    "type": "image_url", 
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
                })

            # 如果沒內容就警告
            if not user_content:
                st.warning("請先輸入一點內容 (錄音、貼圖或打字)！")
                st.session_state.processing = False
                st.stop()

            messages.append({"role": "user", "content": user_content})

            # 2. 呼叫 GPT-4o 進行翻譯
            response = client.chat.completions.create(
                model="gpt-4o", 
                messages=messages,
                response_format={"type": "json_object"} 
            )
            
            result_json = response.choices[0].message.content
            result = json.loads(result_json)
            
            # 3. 生成語音 (OpenAI TTS)
            # 判斷語言來決定語音模型 (越文用 alloy 男聲, 中文用 nova 女聲，或反之)
            if result.get("source_lang") == "vi":
                voice_orig = "alloy"
                voice_trans = "nova"
            else:
                voice_orig = "nova"
                voice_trans = "alloy"

            speech_original = client.audio.speech.create(
                model="tts-1",
                voice=voice_orig,
                input=result["original_text"]
            )
            speech_translated = client.audio.speech.create(
                model="tts-1",
                voice=voice_trans,
                input=result["translated_text"]
            )

            # 4. 存入 Session State
            st.session_state.history = {
                "original": result["original_text"],
                "translated": result["translated_text"],
                "audio_orig": speech_original.content,
                "audio_trans": speech_translated.content
            }

        except Exception as e:
            st.error(f"發生錯誤：{e}")
        
        # 結束處理狀態
        st.session_state.processing = False

# --- 顯示結果區 (左右對照) ---
if st.session_state.history:
    data = st.session_state.history
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("📄 原文內容")
        st.write(data["original"])
        st.audio(data["audio_orig"], format="audio/mp3") 
    
    with col2:
        st.success("🎯 翻譯結果")
        st.write(data["translated"])
        st.audio(data["audio_trans"], format="audio/mp3")
