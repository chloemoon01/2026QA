import streamlit as st
import json
from patent_qa import PatentQAChatbot
from datetime import datetime
import os
import requests

# -------------------------------
# JSON 다운로드 설정
# -------------------------------
JSON_URL = "https://drive.google.com/uc?id=1rlB_4MrzZLFXrwHgPbOQge7bDdinwyKl"
JSON_PATH = "final_patent_chunking_results.json"

def download_json():
    if not os.path.exists(JSON_PATH):
        st.info("📥 특허 데이터 로딩 중입니다. 잠시만 기다려주세요...")
        r = requests.get(JSON_URL)
        r.raise_for_status()
        with open(JSON_PATH, "wb") as f:
            f.write(r.content)

download_json()

# -------------------------------
# 페이지 설정
# -------------------------------
st.set_page_config(
    page_title="Patent QA Chatbot",
    layout="wide"
)

# -------------------------------
# 스타일
# -------------------------------
st.markdown("""
<style>
body {
    background-color: #f5f8fc;
}
.stChatMessage.user {
    background-color: #1f77b4;
    color: white;
    border-radius: 12px;
    padding: 12px;
}
.stChatMessage.assistant {
    background-color: #e3ecf7;
    border-radius: 12px;
    padding: 12px;
}
.meta {
    font-size: 0.8em;
    color: #666;
    margin-top: 6px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 제목
# -------------------------------
st.title("특허 질의응답 시스템")
st.caption("청킹 전략 기반 · 다중 특허 문서 참조 QA")

# -------------------------------
# 챗봇 로딩 (1회)
# -------------------------------
@st.cache_resource
def load_chatbot():
    return PatentQAChatbot(JSON_PATH)

chatbot = load_chatbot()

# -------------------------------
# 세션 상태 초기화
# -------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------------------------------
# 기존 대화 출력 (위)
# -------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and "patents" in msg:
            st.markdown(
                f"<div class='meta'>참조 출원번호: {', '.join(msg['patents'])}</div>",
                unsafe_allow_html=True
            )

# -------------------------------
# 질문 입력 (항상 맨 아래)
# -------------------------------
user_input = st.chat_input("질문을 입력하세요 (예: 이 기술의 주요 장점은 무엇인가요?)")

if user_input:
    # 사용자 질문 저장
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # 답변 생성
    with st.spinner("🤖 답변 생성 중..."):
        result = chatbot.ask(user_input, verbose=False, max_patents=3)

    # 챗봇 답변 저장
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "patents": result["application_numbers"]
    })

    # 즉시 화면 갱신 (입력창 비우기)
    st.rerun()

# -------------------------------
# 요약 정보
# -------------------------------
if st.session_state.messages:
    st.divider()
    st.subheader("📊 응답 요약")
    st.write(f"총 질문 수: {len([m for m in st.session_state.messages if m['role']=='user'])}")
