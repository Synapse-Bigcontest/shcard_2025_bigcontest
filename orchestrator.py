# orchestrator.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any, List, AsyncGenerator

# ⭐️ tools_module에서 analyze_merchant_data 툴만 임포트
from tools_module import analyze_merchant_data 

class AgentOrchestrator:
    def __init__(self, google_api_key: str, llm_config: Dict[str, Any]):
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            google_api_key=google_api_key,
            **llm_config 
        )
        
        # Agent 초기화: analyze_merchant_data 툴만 연결
        self.agent_executor = create_react_agent(self.llm, [analyze_merchant_data])
        
        self.base_system_prompt = (
            "당신은 가맹점 ID 기반 분석 전문 마케팅 컨설턴트입니다. "
            "사용자로부터 받은 입력은 무조건 가맹점 ID(예: '002816BA73')이며, "
            "이 ID를 사용하여 'analyze_merchant_data' Tool을 단 한 번 호출해야 합니다. "
            "최종 응답에는 분석 결과를 표 형태로 명확히 제공하고, 결과를 바탕으로 마케팅 전략을 제시하세요."
        )

    async def astream_response(self, merchant_id: str) -> AsyncGenerator[str, None]:
        """Agent를 비동기로 실행하고 응답을 스트리밍합니다. 입력은 오직 가맹점 ID입니다."""
        
        # 1. 메시지 구성: 시스템 프롬프트 + ID를 포함한 HumanMessage
        full_messages = [
            SystemMessage(content=self.base_system_prompt),
            HumanMessage(content=f"분석을 요청한 가맹점 ID: {merchant_id}") # ID를 명시적으로 전달
        ]

        # 2. Agent 실행
        async for event in self.agent_executor.astream_events({"messages": full_messages}, version="v1"):
            kind = event["event"]
            
            if kind == "on_tool_start":
                tool_name = event["name"]
                tool_input = event["data"].get("input", {})
                
                if tool_name == "analyze_merchant_data":
                    yield f"\n\n**<Tool Call: 📊 상세 분석>**\n가맹점 ID **'{tool_input.get('merchant_id', '...')}**'의 프로필 분석을 시작합니다...\n"
                
            elif kind == "on_tool_end":
                # 툴 결과는 LLM이 처리하도록 숨김
                pass 

            elif kind == "on_chat_model_stream":
                # 최종 LLM 응답을 스트리밍
                content = event["data"]["chunk"].content
                if content:
                    yield content