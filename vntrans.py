import streamlit as st
from openai import OpenAI

# 設定
st.set_page_config(page_title="越轉中字幕", layout="wide")

# 連接 OpenAI
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("API Key 錯誤")
    st.stop()

st.title("🇻🇳 越語 -> 🇹🇼 繁體字幕 (防跳針斬殺版)")

# --- 核心武器：斬殺跳針過濾器 ---
def clean_srt(srt_text):
    blocks = srt_text.strip().split('\n\n')
    clean_blocks = []
    last_txt = ""
    repeat_count = 0
    
    for b in blocks:
        lines = b.split('\n')
        if len(lines) >= 3:
            # 抓出字幕文字
            txt = "\n".join(lines[2:]).strip()
            # 如果跟上一句一樣，開始記數
            if txt == last_txt and len(txt) > 0:
                repeat_count += 1
                # 重複出現第 3 次，直接無視 (不加入結果)
                if repeat_count >= 2: 
                    continue
            else:
                repeat_count = 0
                last_txt = txt
            clean_blocks.append(b)
            
    # 把活下來的字幕重新編號 (1, 2, 3...)
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
        raw_srt = client.audio.transcriptions.create(
            model="whisper-1",
            file=file,
            language="vi",
            response_format="srt"
        )
        
    with st.spinner("2/3 正在斬除跳針當機字幕..."):
        # 呼叫過濾器，把那些 lalaschool 訂閱的廢話砍掉
        filtered_srt = clean_srt(raw_srt)

    with st.spinner("3/3 正在翻譯成繁體中文..."):
        # 簡單安全的 prompt
        sys_msg = "你是字幕翻譯。將越南語字幕翻譯成台灣繁體中文。嚴格保留時間軸，不要改動時間。只輸出字幕內容。"
        
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": filtered_srt}
            ],
            temperature=0.1
        )
        final_srt = res.choices[0].message.content

    st.success("🎉 完成！跳針垃圾已清除。")
    
    # 顯示結果
    c1, c2 = st.columns(2)
    with c1:
        st.text_area("過濾後的越文原稿", filtered_srt, height=400)
    with c2:
        st.text_area("繁體翻譯", final_srt, height=400)
        
    st.download_button("💾 下載繁體字幕", final_srt, "vn_to_tw.srt")
