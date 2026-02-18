import streamlit as st
from openai import OpenAI

# 設定
st.set_page_config(page_title="越轉中字幕", layout="centered")

# 連接 OpenAI
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("API Key 設定有誤")
    st.stop()

st.title("🇻🇳 越語音檔 -> 🇹🇼 繁體字幕")

# 上傳檔案
file = st.file_uploader("上傳越語 MP3/M4A/WAV", type=["mp3", "m4a", "wav"])

if file and st.button("🚀 開始製作"):
    with st.spinner("1/2 正在聽寫越南語原文..."):
        # 第一步：只聽寫越文 (避免亂碼)
        raw = client.audio.transcriptions.create(
            model="whisper-1",
            file=file,
            language="vi", # 指定越南語
            response_format="srt"
        )

    with st.spinner("2/2 正在翻譯成繁體中文..."):
        # 第二步：GPT-4o 翻譯
        # 這裡用最簡單的字串拼接，防止格式錯誤
        prompt = "你是一個字幕翻譯。將底下的越南語字幕翻譯成台灣繁體中文。保留時間軸。直接輸出字幕內容。"
        
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": raw}
            ]
        )
        final_srt = res.choices[0].message.content

    st.success("完成！")
    
    # 顯示結果
    c1, c2 = st.columns(2)
    with c1:
        st.text_area("越文原稿", raw, height=300)
    with c2:
        st.text_area("繁體翻譯", final_srt, height=300)
        
    st.download_button("下載字幕", final_srt, "vn_to_tw.srt")
