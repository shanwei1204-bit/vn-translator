import streamlit as st
from openai import OpenAI
import re

st.set_page_config(page_title="SRT 字幕生成 (終極過濾版)", layout="centered")

try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    st.error("請檢查 Secrets 中的 API Key")
    st.stop()

st.title("🎬 MP3 轉 繁體 SRT 字幕 (斬殺跳針版)")
st.warning("已內建「物理幻覺過濾器」，專門對付無聲片段的無限跳針 Bug。")

# --- 核心除錯工具：自動斬殺無限重複的字幕 ---
def filter_hallucinations(srt_content):
    blocks = srt_content.strip().split('\n\n')
    cleaned_blocks = []
    last_text = ""
    repeat_count = 0
    
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            # 抓出字幕的文字部分
            text = "\n".join(lines[2:]).strip()
            
            # 如果跟上一句一模一樣，開始計數
            if text == last_text and len(text) > 0:
                repeat_count += 1
                # 容忍講話結巴重複 1 次，連續第 3 次一模一樣直接殺掉 (跳過不寫入)
                if repeat_count >= 2:  
                    continue
            else:
                repeat_count = 0
                last_text = text
            
            cleaned_blocks.append(block)
            
    # 斬殺完畢後，重新把 SRT 的序號 (1, 2, 3...) 排列整齊
    final_srt = []
    for i, block in enumerate(cleaned_blocks):
        lines = block.split('\n')
        if len(lines) >= 3:
            lines[0] = str(i + 1)
            final_srt.append("\n".join(lines))
            
    return "\n\n".join(final_srt)

# --- 主介面 ---
uploaded_file = st.file_uploader("請上傳音檔 (MP3/M4A/WAV, 25MB以內)", type=["mp3", "m4a", "wav"])

if uploaded_file:
    if st.button("🚀 開始製作字幕", type="primary"):
        progress_bar = st.progress(0)
        status = st.empty()
        
        try:
            # 階段 1: 讓 Whisper 聽寫
            status.text("1/3 正在聽寫音檔 (Whisper)...")
            progress_bar.progress(30)
            
            raw_srt = client.audio.transcriptions.create(
                model="whisper-1", 
                file=uploaded_file, 
                response_format="srt"
            )
            
            # 階段 2: 程式介入，物理斬殺跳針
            status.text("2/3 正在斬除無限重複的當機字幕 (Python 過濾器)...")
            progress_bar.progress(60)
            
            filtered_srt = filter_hallucinations(raw_srt)
            
            # 階段 3: GPT-4o 轉繁體，並賦予刪除權力
            status.text("3/3 轉換標準繁體中文 (GPT-4o)...")
            progress_bar.progress(85)
            
            # 這次我把「絕對不能刪除」的愚蠢指令拿掉了！
            sys_prompt = "你是一個專業台灣字幕編輯。請將輸入的 SRT 轉為繁體中文。保留時間軸。如果發現無意義的單字或明顯的亂碼，請直接大膽刪除那一段。"
            
            res = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": filtered_srt}
                ],
                temperature=0.1
            )
            final_srt = res.choices[0].message.content
            
            progress_bar.progress(100)
            status.success("🎉 製作完成！跳針已全數清除。")
            
            st.text_area("字幕預覽", final_srt, height=300)
            st.download_button("💾 下載乾淨的繁體 .srt", final_srt, file_name="clean_subtitle.srt", mime="text/plain")
            
        except Exception as e:
            st.error(f"發生錯誤：{e}")
