import streamlit as st
from openai import OpenAI

# 設定
st.set_page_config(page_title="越轉中字幕", layout="wide")

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("API Key 錯誤")
    st.stop()

st.title("🇻🇳 越語 -> 🇹🇼 繁體字幕 (極限斬殺版)")

# --- 核心武器：極限斬殺過濾器 ---
def clean_srt(srt_text):
    blocks = srt_text.strip().split('\n\n')
    clean_blocks = []
    last_txt = ""
    
    for b in blocks:
        lines = b.split('\n')
        if len(lines) >= 3:
            # 抓出字幕文字
            txt = "\n".join(lines[2:]).strip()
            
            # 【零容忍】：只要跟上一句一樣，立刻刪除，絕不留第2句
            if txt == last_txt and len(txt) > 0:
                continue
                
            # 【幻覺特殺】：針對影片的「訂閱廣告」或常見幻覺直接刪除
            if "lalaschool" in txt.lower() or "đăng kí" in txt.lower():
                continue
                
            last_txt = txt
            clean_blocks.append(b)
            
    # 把存活下來的字幕重新排好序號 (1, 2, 3...)
    res = []
    for i, b in enumerate(clean_blocks):
        lines = b.split('\n')
        if len(lines) >= 3:
            lines[0] = str(i + 1)
            res.append("\n".join(lines))
    return "\n\n".join(res)

# 主程式
file = st.file_uploader("上傳越語音檔 (MP3/M4A/WAV)", type=["mp3", "m4a", "wav"])

if file and st.button("🚀 開始製作", type="primary"):
    with st.spinner("1/3 正在聽寫越文..."):
        # 加上 temperature=0.2 降低 AI 亂作夢的機率
        raw_srt = client.audio.transcriptions.create(
            model="whisper-1",
            file=file,
            language="vi",
            response_format="srt",
            temperature=0.2
        )
        
    with st.spinner("2/3 極限斬除跳針與廣告..."):
        filtered_srt = clean_srt(raw_srt)
        
        # 防呆：如果過濾完發現整首都是音樂，沒半句真話
        if not filtered_srt.strip():
            st.warning("⚠️ 分析完畢：這段影片似乎完全沒有人講話，或者全部都是背景音樂/雜音。")
            st.stop()

    with st.spinner("3/3 正在翻譯
