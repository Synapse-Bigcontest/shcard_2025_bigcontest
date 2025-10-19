# orchestrator.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from typing import Dict, Any, List, AsyncGenerator, Union

class AgentOrchestrator:
    """
    이 클래스는 툴 호출(analyze_merchant_data)이 완료된 후, 
    ToolMessage를 포함한 전체 대화 기록을 받아 Gemini LLM에게 전달하여
    최종 컨설팅 답변을 스트리밍으로 생성하는 역할을 수행합니다.
    """
    
    def __init__(self, google_api_key: str, llm_config: Dict[str, Any]):
        # TODO: 규칙 1에 따라 최종 제출 시 'gemini-2.5-flash'로 변경해야 함
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro", 
            google_api_key=google_api_key,
            temperature=llm_config.get("temperature", 0.1) # 낮은 온도로 일관된 컨설팅 답변 유도
        )
        
    async def astream(self, input_data: dict) -> AsyncGenerator[str, None]:
        """
        비동기적으로 LLM을 호출하고 응답을 스트리밍합니다.
        
        Args:
            input_data: {"messages": [SystemMessage, HumanMessage, AIMessage(ToolCall), ToolMessage, ...]} 형태의 딕셔너리
        
        Yields:
            응답 텍스트 청크(chunk)
        """
        messages: List[Union[SystemMessage, HumanMessage, ToolMessage]] = input_data.get("messages", [])
        
        try:
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    yield chunk.content
            
        except Exception as e:
            print(f"LLM Astream 내부 오류: {e}")
            yield "LLM 응답 생성 중 예상치 못한 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."