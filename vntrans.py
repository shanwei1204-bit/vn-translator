import streamlit as st
from openai import OpenAI
from collections import Counter

st.set_page_config(layout="wide")

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("API Key Error")
    st.stop()

st.title("🇻🇳 越語轉繁體字幕 (終極版)")

# --- 全局必殺過濾器 ---
def clean_srt(raw_str):
    blocks = raw_str.strip().split('\n\n')
    
    # 抓出所有文字來統計
    texts = []
    for b in blocks:
        lines = b.split('\n')
        if len(lines) > 2:
            texts.append("\n".join(lines[2:]).strip())
            
    # 計算每句話在整部影片出現的次數
    freq = Counter([t for t in texts if t])
    
    clean_blocks = []
    for b in blocks:
        lines = b.split('\n')
        if len(lines) > 2:
            txt = "\n".join(lines[2:]).strip()
            txt_low = txt.lower()
            
            # 【黑名單】：看到直接殺
            if "lalaschool" in txt_low:
                continue
            if "đăng kí" in txt_low:
                continue
                
            # 【全局跳針】：長度大於10個字，且出現超過1次，全部殺
            if len(txt) > 10 and freq[txt] > 1:
                continue
                
            clean_blocks.append(b)
            
    # 重新編排序號
    res = []
    for i, b in enumerate(clean_blocks):
        lines = b.split('\n')
        if len(lines) > 2:
            lines[0] = str(i + 1)
            res.append("\n".join(lines))
            
    return "\n\n".join(res)

# --- 主程式 ---
file = st.file_uploader("Upload", type=["mp3", "m4a", "wav"])

if file and st.button("Start"):
    # 用最簡單的語法，防止複製被切斷
    st.info("步驟 1/3: 聽寫中...")
    raw = client.audio.transcriptions.create(
        model="whisper-1",
        file=file,
        language="vi",
        response_format="srt",
        temperature=0.2
    )
    
    st.info("步驟 2/3: 過濾跳針與廣告...")
    cleaned = clean_srt(raw)
    
    if not cleaned.strip():
        st.warning("這段影片無人聲或全都是垃圾廣告。")
        st.stop()
        
    st.info("步驟 3/3: 翻譯繁體中文...")
    # 把字串拆短，防止你複製時出錯
    p1 = "你是字幕翻譯。將越文翻譯成台灣繁體中文。"
    p2 = "保留時間軸格式，只輸出字幕。"
    sys_msg
