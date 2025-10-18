# streamlit_app.py (챗봇 UI 복구 버전)

import streamlit as st
import os
import asyncio
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from pathlib import Path

# ⭐️⭐️⭐️ 모듈 임포트 ⭐️⭐️⭐️
try:
    from orchestrator import AgentOrchestrator
    from data_processor import DF_MERGED 
except ImportError as e:
    st.error(f"필수 모듈 로드 오류: {e}. 경로와 파일명을 확인하세요.")
    AgentOrchestrator = None
    DF_MERGED = None


# --- 환경 변수 및 초기 설정 ---
system_prompt = "당신은 친절한 마케팅 상담사입니다. 사용자로부터 받은 첫 메시지에서 **가맹점 ID(예: '002816BA73')**를 추출하여 **analyze_merchant_data** 툴을 호출하세요. ID 추출에 실패하면 사용자에게 ID를 다시 요청하세요. 최종 응답에는 분석 결과를 표로 요약하고 마케팅 전략을 제시합니다."
greeting = "안녕하세요! 분석을 원하는 **가맹점 ID(예: 002816BA73)**를 입력해주세요. ID를 기반으로 상세 분석을 도와드리겠습니다."


# --- Helper Functions ---
def clear_chat_history():
    st.session_state.messages = [SystemMessage(content=system_prompt), AIMessage(content=greeting)]

def render_chat_message(role: str, content: str):
    with st.chat_message(role):
        st.markdown(content)

# --- Page Config ---
st.set_page_config(page_title="신한카드 AI 컨설턴트 (챗봇)", page_icon="🎈", layout="wide")

def main():
    # --- UI & 초기화 ---
    st.title("신한카드 소상공인 🔑 비밀상담소 (챗봇)")
    
    with st.sidebar:
        st.button('Clear Chat History', on_click=clear_chat_history)
            
    # API Key Check
    try:
        if "GOOGLE_API_KEY" not in os.environ and "GOOGLE_API_KEY" in st.secrets:
            os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
        GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
        if not GOOGLE_API_KEY:
            st.error("GOOGLE_API_KEY 환경 변수 또는 secrets.toml에 키가 설정되지 않았습니다.")
            return

    except Exception:
        st.error("GOOGLE_API_KEY 설정 중 오류가 발생했습니다.")
        return

    # Agent Orchestrator 초기화
    if AgentOrchestrator is None: return
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = AgentOrchestrator(
            google_api_key=GOOGLE_API_KEY,
            llm_config={"temperature": 0.1}
        )
    
    # 메시지 상태 초기화
    if "messages" not in st.session_state:
        clear_chat_history()
    
    # 데이터 로드 확인
    if DF_MERGED is not None and DF_MERGED.empty:
        st.error("데이터 (`DF_MERGED`) 로드에 실패했습니다. 'preprocess_data.py'를 실행했는지 확인하세요.")
        return

    # 대화 히스토리 화면 표시
    for message in st.session_state.messages:
        if not isinstance(message, SystemMessage):
            render_chat_message(
                "user" if isinstance(message, HumanMessage) else "assistant", 
                message.content
            )
            
    # ----------------------------------------------------
    # --- 사용자 입력 처리 (메인 채팅 루프) ---
    # ----------------------------------------------------

    if query := st.chat_input("가맹점 ID를 입력하고 엔터를 누르세요"):
        
        # 1. 사용자 메시지 추가
        st.session_state.messages.append(HumanMessage(content=query))
        render_chat_message("user", query)

        # 2. Agent 실행 및 스트리밍
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            orchestrator = st.session_state.orchestrator
            
            try:
                # 3. 입력 메시지 준비 (SystemMessage 제외)
                # Agent는 전체 대화 히스토리 대신, 사용자의 '현재' 입력(query)을 ID로 처리하도록 오케스트레이터가 구성됨.
                # 하지만 Agent 실행 루프는 메시지 리스트를 받으므로, ID 추출을 위해 쿼리를 그대로 전달합니다.
                
                # 4. 비동기 실행 및 스트리밍
                # ⭐️⭐️⭐️ 오류 수정: asyncio.run() 내에서 async for를 사용하여 리스트로 만듭니다. ⭐️⭐️⭐️
                
                # 제너레이터를 코루틴으로 감싸서 리스트로 변환하는 함수 정의
                async def run_generator_to_list():
                    stream = orchestrator.astream_response(merchant_id=query)
                    return [chunk async for chunk in stream]
                
                # asyncio.run()을 사용하여 코루틴 실행
                chunk_list = asyncio.run(run_generator_to_list())
                
                # 리스트의 내용을 순차적으로 표시 (스트리밍 효과 유지)
                for chunk in chunk_list:
                    full_response += chunk
                    placeholder.markdown(full_response + "▌") # 커서 표시
                
                placeholder.markdown(full_response) # 최종 응답 표시

                # 6. AI 응답을 대화 히스토리에 추가
                st.session_state.messages.append(AIMessage(content=full_response))
            
            except RuntimeError as e:
                error_msg = f"**🚨 Streamlit 실행 오류:** {e!r} (비동기 함수 호출 문제). 다시 시도해 주세요."
                st.error(error_msg)
                st.session_state.messages.append(AIMessage(content=f"오류가 발생하여 상담을 계속할 수 없습니다. 다시 시도해 주세요."))
            except Exception as e:
                error_msg = f"**🚨 Agent 실행 중 오류 발생:** {e!r}"
                st.error(error_msg)
                st.session_state.messages.append(AIMessage(content=f"오류가 발생하여 상담을 계속할 수 없습니다. 다시 시도해 주세요."))


if __name__ == "__main__":
    main()