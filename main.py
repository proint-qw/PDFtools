import streamlit as st
import os
from langchain.memory import ConversationBufferMemory
from utils import qa_agent

st.title("📑 AI智能PDF问答工具")

with st.sidebar:
    # 获取环境变量密钥（供您自己使用）
    env_key = os.getenv("OPENAI_API_KEY", "")

    # 用户输入框（其他人使用）
    openai_api_key = st.text_input(
        "请输入OpenAI API密钥：",
        type="password",
        value=env_key,  # 如果您配置了环境变量，输入框自动填充
        help="管理员已配置密钥时可留空" if env_key else None
    )

    # 提示信息
    if env_key:
        st.info("ℹ️ 检测到预配置密钥，输入框可留空直接使用")
    st.markdown("[获取OpenAI API key](https://platform.openai.com/account/api-keys)")

# 强制检查密钥
if not openai_api_key and not env_key:
    st.error("❌ 需要提供OpenAI API密钥（输入或环境变量）")
    st.stop()

# 初始化会话内存
if "memory" not in st.session_state:
    st.session_state["memory"] = ConversationBufferMemory(
        return_messages=True,
        memory_key="chat_history",
        output_key="answer"
    )

# 文件上传和提问
uploaded_file = st.file_uploader("上传你的PDF文件：", type="pdf")
question = st.text_input("对PDF的内容进行提问", disabled=not uploaded_file)

if uploaded_file and question:
    with st.spinner("AI正在思考中，请稍等..."):
        response = qa_agent(
            openai_api_key or env_key,  # 合并最终密钥
            st.session_state["memory"],
            uploaded_file,
            question
        )
    st.write("### 答案")
    st.write(response["answer"])
    st.session_state["chat_history"] = response["chat_history"]

# 历史消息展示
if "chat_history" in st.session_state:
    with st.expander("历史消息"):
        for i in range(0, len(st.session_state["chat_history"]), 2):
            human_message = st.session_state["chat_history"][i]
            ai_message = st.session_state["chat_history"][i + 1]
            st.write(f"用户：{human_message.content}")
            st.write(f"AI：{ai_message.content}")
            if i < len(st.session_state["chat_history"]) - 2:
                st.divider()