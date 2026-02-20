import streamlit as st
from openai import OpenAI
from collections import Counter

st.set_page_config(layout="wide")

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("API Key Error")
    st.stop()

st.title("🇻🇳 越語轉繁體字幕 (終極防錯版)")

def clean_srt(raw_str):
    blocks = raw_str.strip().split('\n\n')
    texts = []
    for b in blocks:
        lines = b.split('\n')
        if len(lines) > 2:
            texts.append("\n".join(lines[2:]).strip())
            
    freq = Counter([t for t in texts if t])
    clean_blocks = []
    for b in blocks:
        lines = b.split('\n')
        if len(lines) > 2:
            txt = "\n".join(lines[2:]).strip()
            txt_low = txt.lower()
            if "lalaschool" in txt_low or "đăng kí" in txt_low:
                continue
            if len(txt) > 10 and freq[txt] > 1:
                continue
            clean_blocks.append(b)
            
    res = []
    for i, b in enumerate(clean_blocks):
        lines = b.split('\n')
        if len(lines) > 2:
            lines[0] = str(i + 1)
            res.append("\n".join(lines))
    return "\n\n".join(res)

file = st.file_uploader("Upload", type=["mp3", "m4a", "wav"])

if file and st.button("Start"):
    # 【新增防呆】：檢查檔案是否超過 25MB (25 * 1024 * 1024 bytes)
    if file.size > 26214400:
        st.error("❌ 檔案太大了！OpenAI 限制最高只能上傳 25MB 的音檔，請先將音檔壓縮或剪輯。")
        st.stop()

    st.info("步驟 1/3: 聽寫中...")
    try:
        # 【新增防呆】：強制讀取檔案名稱與位元組，避免 OpenAI 認不出檔案
        raw = client.audio.transcriptions.create(
            model="whisper-1",
            file=(file.name, file.read()), 
            language="vi",
            response_format="srt",
            temperature=0.2
        )
    except Exception as e:
        st.error(f"❌ OpenAI 語音辨識發生錯誤：\n{e}")
        st.stop()
    
    st.info("步驟 2/3: 過濾跳針與廣告...")
    cleaned = clean_srt(raw)
    
    if not cleaned.strip():
        st.warning("影片無人聲或全都是垃圾廣告。")
        st.stop()
        
    st.info("步驟 3/3: 翻譯繁體中文...")
    try:
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "你是字幕翻譯。將越文翻譯成台灣繁體中文。保留時間軸格式，只輸出字幕。"},
                {"role": "user", "content": cleaned}
            ],
            temperature=0.1
        )
        final_srt = res.choices[0].message.content
    except Exception as e:
        st.error(f"❌ OpenAI 翻譯發生錯誤：\n{e}")
        st.stop()
        
    st.success("🎉 完成！")
    
    c1, c2 = st.columns(2)
    with c1:
        st.text_area("過濾後的越文", cleaned, height=400)
    with c2:
        st.text_area("繁體中文", final_srt, height=400)
        
    st.download_button("下載字幕", final_srt, "sub.srt")
