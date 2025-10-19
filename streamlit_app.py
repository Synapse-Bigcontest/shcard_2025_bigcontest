# streamlit_app.py

import streamlit as st
import os
import asyncio
import nest_asyncio # ⭐️ nest_asyncio 추가 (비동기 오류 해결)
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage, ToolMessage
import json
import platform 
from typing import List, Union, AsyncGenerator 

# ⭐️⭐️⭐️ 모듈 임포트 (실제 파일을 임포트해야 합니다) ⭐️⭐️⭐️
try:
    from orchestrator import AgentOrchestrator
    from modules.visualization import create_visualization 
    from data_processor import DF_MERGED 
    from tools_module import analyze_merchant_data 
except ImportError as e:
    st.error(f"필수 모듈 로드 오류: {e}. 경로와 파일명을 확인하세요. (langchain, streamlit, pandas, modules 확인)")
    AgentOrchestrator = None
    DF_MERGED = None
    # 로드 실패 시 analyze_merchant_data도 None으로 설정 (아래에서 예외 처리됨)
    analyze_merchant_data = None
    create_visualization = lambda analysis_data_json_string: st.error("시각화 모듈 로드 실패. 'modules/visualization.py' 파일을 확인하세요.") 

# --- 환경 변수 및 초기 설정 ---
system_prompt = (
    "당신은 가맹점 데이터 분석 전문 컨설턴트입니다. 고객님이 입력한 가맹점 ID에 대한 상세 분석 결과(`ToolMessage`)를 기반으로 다음 지침을 따라 종합 컨설팅 답변을 제공하세요. "
    "1. **가맹점 정보 사용**: `ToolMessage` JSON 내부의 '가맹점ID'와 **'가맹점명'**을 **반드시 그대로 사용하여** 응답을 시작하세요. 외부 지식을 사용하거나 다른 가맹점명을 언급하지 마세요. "
    "2. **응답 구성**: 분석 요약 및 시각화 결과가 이미 위에 표시되었음을 언급하며, 다음 3가지 핵심 항목을 상세히 분석하여 제공하세요:\n"
    "   - **매출 및 경쟁력 분석**: 상권 및 업종 대비 순위와 월 매출 수준을 해석하여 경쟁력 수준을 평가합니다.\n"
    "   - **고객 구조 분석**: '주요 고객 유형' 및 시각화된 고객층 데이터를 기반으로 핵심 타겟층을 정의하고 특징을 설명합니다.\n"
    "   - **마케팅 전략 제언**: 신규/재방문율 및 고객 구조 분석을 바탕으로 구체적인 마케팅 또는 운영 개선 전략 2~3가지를 제안합니다."
)
greeting = "안녕하세요! 분석을 원하는 **가맹점 ID**를 입력해주세요. 상세 분석을 도와드리겠습니다.\n\n**[사용 가능한 예시 ID]**\n- `002816BA73` (카페/디저트)\n- `009988C7D6` (한식)"


# --- Helper Functions ---
def clear_chat_history():
    """채팅 기록을 시스템 프롬프트와 인사말로 초기화합니다."""
    st.session_state.messages = [SystemMessage(content=system_prompt), AIMessage(content=greeting)]

def render_chat_message(role: str, content: str):
    """채팅 메시지를 렌더링합니다."""
    with st.chat_message(role):
        st.markdown(content)

def get_llm_response_stream(orchestrator, messages: List[Union[SystemMessage, AIMessage, HumanMessage, ToolMessage]]):
    """
    LLM의 비동기 스트림(`orchestrator.astream`)을 Streamlit 환경에 맞게 안전하게 동기 실행하고, 
    스트리밍 결과를 Streamlit에 출력합니다.
    """
    
    placeholder = st.empty()
    full_response = ""
    
    # LLM 스트리밍을 처리하는 비동기 함수 정의
    async def run_llm_stream():
        nonlocal full_response
        
        stream_generator: AsyncGenerator[str, None] = orchestrator.astream({"messages": messages})
        
        async for chunk in stream_generator:
            full_response += chunk
            await asyncio.sleep(0.001) 
            placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)


    # ⭐️ 동기적으로 비동기 함수를 실행하고 결과를 얻습니다. (nest_asyncio 적용) ⭐️
    try:
        # 1. 현재 이벤트 루프 가져오기
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # 2. 비동기 함수 실행 및 완료 대기
        loop.run_until_complete(run_llm_stream())
        
    except Exception as e:
        # LLM 호출 실패 시
        st.error(f"LLM 응답 생성 중 오류가 발생했습니다: {e!r}")
        return

    # 대화 기록에 최종 답변을 저장합니다.
    if full_response:
        st.session_state.messages.append(AIMessage(content=full_response))
    else:
        st.session_state.messages.append(AIMessage(content="컨설팅 응답을 생성하지 못했습니다."))


# --- Page Config ---
st.set_page_config(page_title="신한카드 AI 컨설턴트 (챗봇)", page_icon="🎈", layout="wide")

def main():
    
    # ⭐️⭐️⭐️ nest_asyncio 적용 (비동기 오류 해결) ⭐️⭐️⭐️
    nest_asyncio.apply()
    
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
    # DF_MERGED가 None이 아니면서, .empty 속성이 있고 그 값이 True일 때 (데이터 로드 실패)
    if DF_MERGED is not None and (hasattr(DF_MERGED, 'empty') and DF_MERGED.empty):
        st.error("데이터 (`DF_MERGED`) 로드에 실패했습니다. 'data_processor.py' 실행을 확인하세요.")
        return

    # 대화 히스토리 화면 표시
    for message in st.session_state.messages:
        if not isinstance(message, (SystemMessage, ToolMessage)):
            render_chat_message(
                "user" if isinstance(message, HumanMessage) else "assistant", 
                message.content
            )
            
    # --- 사용자 입력 처리 (메인 채팅 루프) ---

    if query := st.chat_input("가맹점 ID를 입력하고 엔터를 누르세요"):
        
        input_id = query.strip()
        # 1. 사용자 입력 메시지를 히스토리에 추가
        st.session_state.messages.append(HumanMessage(content=query))
        render_chat_message("user", query)

        result_container = st.container()

        # 2. 툴 함수 추출 및 직접 동기 호출 
        if analyze_merchant_data is None:
            result_container.error("❌ 툴 모듈이 로드되지 않았습니다.")
            return

        try:
            with st.spinner(f"가맹점 ID '{input_id}'의 데이터를 검색 중..."):
                # analyze_merchant_data는 툴 객체이므로 .func를 통해 실제 함수를 호출합니다.
                tool_function = analyze_merchant_data.func 
                tool_result = tool_function(input_id)
        except Exception as e:
            result_container.error(f"❌ 툴 실행 중 오류가 발생했습니다: {type(e).__name__}(). 상세: {str(e)}")
            return

        if not tool_result.get("found"):
            error_message = tool_result.get("message", "데이터 검색에 실패했습니다.")
            result_container.error(f"❌ 데이터 로드 실패: **{error_message}**")
            st.session_state.messages.append(AIMessage(content=f"데이터 검색 실패: {error_message}"))
            return
        
        # 3. 데이터 찾기 성공 시 성공 메시지 출력
        result_container.success(f"✅ 가맹점 ID '{input_id}'의 데이터가 성공적으로 검색되었습니다. 아래 **가맹점 분석 요약 및 시각화 결과**를 확인해주세요.")

        # 4. 툴 결과 및 AI 메시지 구성 (LLM 컨텍스트 구성)
        analysis_data_json_string = tool_result.get("analysis_data", "{}")
        
        # 4-1. 툴 호출을 가정하는 AIMessage 생성 (컨텍스트 명확화)
        tool_call_id = "custom-tool-call" 
        ai_message_with_tool_call = AIMessage(
            content="", 
            tool_calls=[{"id": tool_call_id, "name": "analyze_merchant_data", "args": {"merchant_id": input_id}}]
        )

        # 4-2. 툴 결과 메시지 생성
        tool_message = ToolMessage(
            content=analysis_data_json_string,
            tool_call_id=tool_call_id 
        )
        
        # ⭐️⭐️⭐️⭐️⭐️ 디버깅 코드 (콘솔 출력) ⭐️⭐️⭐️⭐️⭐️
        print("="*60)
        print(f"✅ ToolMessage 생성 완료 - ID: {input_id}")
        print("🔎 ToolMessage Content (분석 데이터):") 
        print(tool_message.content[:500] + "..." if len(tool_message.content) > 500 else tool_message.content)
        print("="*60)
        # ⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️⭐️

        # ⭐️⭐️⭐️ LLM에게 전달할 메시지 목록 (수정된 논리적 흐름) ⭐️⭐️⭐️
        messages_for_llm = [
            st.session_state.messages[0], # SystemMessage
            HumanMessage(content=query),  # 현재의 사용자 입력
            ai_message_with_tool_call,    # AI가 툴 호출을 했다고 '가정'
            tool_message                  # 툴 호출의 결과 데이터 (핵심 컨텍스트)
        ]
        
        # UI 채팅 기록에는 AIMessage(ToolCall)과 ToolMessage를 추가
        st.session_state.messages.append(ai_message_with_tool_call)
        st.session_state.messages.append(tool_message)

        # 5. 시각화 데이터 추출 및 표시
        with result_container:
            if create_visualization:
                create_visualization(analysis_data_json_string) 
        
        # 6. LLM 스트리밍 함수 호출
        with st.chat_message("assistant"):
            st.info("AI 컨설턴트가 분석 결과를 기반으로 컨설팅 중입니다. 잠시만 기다려 주세요.")
            get_llm_response_stream(
                orchestrator=st.session_state.orchestrator,
                messages=messages_for_llm 
            )


if __name__ == "__main__":
    main()