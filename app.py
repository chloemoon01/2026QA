import streamlit as st
import json
from patent_qa import PatentQAChatbot  # 기존 코드 파일명 기준
from datetime import datetime

# -------------------------------
# 페이지 설정
# -------------------------------
st.set_page_config(
    page_title="Patent QA Chatbot",
    layout="wide"
)

# -------------------------------
# 스타일 (파란색, 좌우 채팅)
# -------------------------------
st.markdown("""
<style>
body {
    background-color: #f5f8fc;
}

.chat-container {
    max-width: 900px;
    margin: auto;
}

.user-msg {
    background-color: #1f77b4;
    color: white;
    padding: 12px;
    border-radius: 12px;
    margin: 10px 0;
    text-align: right;
}

.bot-msg {
    background-color: #e3ecf7;
    color: black;
    padding: 12px;
    border-radius: 12px;
    margin: 10px 0;
    text-align: left;
}

.meta {
    font-size: 0.8em;
    color: #666;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# 제목
# -------------------------------
st.title("🔍 특허 질의응답 시스템")
st.caption("청킹 전략 기반 · 다중 특허 문서 참조 QA")

# -------------------------------
# 챗봇 로딩 (1회)
# -------------------------------
@st.cache_resource
def load_chatbot():
    return PatentQAChatbot("final_patent_chunking_results.json")


chatbot = load_chatbot()

# -------------------------------
# 세션 상태 초기화
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------------------
# 질문 입력
# -------------------------------
question = st.text_input("질문을 입력하세요", placeholder="예: 이 기술의 주요 장점은 무엇인가요?")

if st.button("질문하기") and question.strip():
    result = chatbot.ask(question, verbose=False, max_patents=3)
    
    st.session_state.chat_history.append({
        "question": question,
        "answer": result["answer"],
        "patents": result["application_numbers"],
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

# -------------------------------
# 채팅 히스토리 출력
# -------------------------------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for chat in st.session_state.chat_history:
    st.markdown(f"""
    <div class="user-msg">
        {chat['question']}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="bot-msg">
        {chat['answer']}
        <div class="meta">참조 출원번호: {", ".join(chat['patents'])}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------
# 간단한 시각화 (신뢰도용)
# -------------------------------
if st.session_state.chat_history:
    st.subheader("📊 응답 정보 요약")
    st.write(f"총 질문 수: {len(st.session_state.chat_history)}")
