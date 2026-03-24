import streamlit as st
from openai import OpenAI

# 頁面基本設定
st.set_page_config(page_title="北越即時語音翻譯官 v1.2", page_icon="🇻🇳")

st.title("🇻🇳 北越即時語音翻譯官")
st.markdown("---")

# 從側邊欄讀取 OpenAI API Key
with st.sidebar:
    st.header("設定")
    api_key = st.text_input("請輸入 OpenAI API Key", type="password")
    st.info("此翻譯機專攻北越河內口音，並自動附帶語氣註解。")

if api_key:
    client = OpenAI(api_key=api_key)

    # 核心翻譯指令 (System Prompt)
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "system", 
                "content": (
                    "你現在是「語音翻譯機器人 v1.2」。"
                    "角色：北越即時語音翻譯官。"
                    "語言：繁體中文 & 北越方言 (Hanoi Accent)。"
                    "規則："
                    "1. 中翻越：提供「越南文 (北越)」+「中文單字註解」。"
                    "2. 越翻中：提供「中文翻譯」+「語氣標註 (放在註解區)」。"
                    "3. 詞彙偏好：使用北越詞彙（如 Chè, Bát, Vào, Ở đây）。"
                    "4. 嚴格遵守：不廢話、不給多餘建議、不擅自加入額外評論。"
                    "5. 註解格式：必須列出單字含義與語氣性質。"
                )
            }
        ]

    # 顯示對話紀錄
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # 使用者輸入
    if prompt := st.chat_input("請輸入文字..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 呼叫 OpenAI API
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.messages,
                temperature=0.3 # 降低隨機性，確保翻譯精準
            )
            answer = response.choices[0].message.content
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
else:
    st.warning("⚠️ 請先在左側欄位輸入 OpenAI API Key 才能開始翻譯。")
