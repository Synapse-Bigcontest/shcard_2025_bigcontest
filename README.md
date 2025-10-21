# 🎈 AI 축제 컨설턴트 (Agentic RAG)

## Agentic RAG 기반 소상공인 맞춤형 지역 축제 컨설팅 시스템
## 축제 추천 방식 수정 예정, 503 500 에러는 gemini 모델의 문제라... 잠시 쉬었다가 다시 테스트하는 방법 밖에 없는듯

신한카드 빅데이터와 전국 축제 정보를 통합 분석하여, AI 에이전트가 가게별로 참여할 만한 지역 축제와 최적의 마케팅 전략 보고서를 자동 생성합니다.

---

## 🧭 프로젝트 개요

이 프로젝트는 **Streamlit 웹 인터페이스 + FastAPI 데이터 서버 + LangChain 에이전트**로 구성된 AI 컨설팅 자동화 시스템입니다.

사용자는 자신의 가게를 선택하여 상세 프로필을 확인한 뒤,  
예를 들어 **"20대 여성 고객을 늘리고 싶어"** 또는 **"근처 축제 추천해줘"** 와 같은 자연어 질문을 입력할 수 있습니다.

AI 에이전트(Orchestrator)는 이 질문을 이해하고, 가게의 상세 프로필(JSON)을 컨텍스트로 삼아 **가장 적절한 도구(Tool)** 를 스스로 선택하고 실행합니다.

### 🔧 예시 흐름
- (축제 추천) → `recommend_festivals` → FAISS 벡터 검색 + LLM 재평가(Re-ranking)
- (마케팅 전략) → `search_contextual_marketing_strategy` → 마케팅 RAG
- (가게 분석) → `analyze_merchant_profile` → LLM 기반 SWOT 분석
- (축제 분석) → `analyze_festival_profile` → LLM 기반 축제 요약

최종적으로, 에이전트는 도구 실행 결과를 바탕으로 자연스러운 한국어 컨설팅 답변을 생성하여 사용자에게 제공합니다.

---

## 📂 프로젝트 구조

```bash
AI_FESTIVAL_CONSULTANT/
├── orchestrator.py           # AI 에이전트 (Tool-Calling Agent)
├── streamlit_app.py          # Streamlit 웹 인터페이스 (UI)
│
├── api/
│   ├── server.py             # FastAPI 데이터 서버
│   └── data_loader.py        # 데이터 로드 및 전처리
│
├── modules/
│   ├── knowledge_base.py     # RAG 및 벡터 스토어 로더
│   ├── filtering.py          # [Tool] 축제 추천 (FAISS + LLM)
│   ├── tool_definitions.py   # [Tool] 마케팅, SWOT 등 기타 도구
│   ├── profile_utils.py      # 가맹점 프로필 JSON 유틸리티
│   ├── visualization.py      # Streamlit 시각화 모듈
│   └── llm_provider.py       # LLM 인스턴스 관리
│
└── data/
    ├── final_df.csv          # 가맹점 데이터
    └── festival_df.csv       # 축제 정보 데이터
└── vectorstore/
    ├── faiss_festival        # 축제 벡터 DB
    └── faiss_marketing       # 마케팅 벡터 DB
```

---

## 🔄 아키텍처 및 데이터 흐름

이 시스템은 **"에이전트 중심의 도구 호출(Tool-Calling)"** 아키텍처를 기반으로 작동합니다.  
사용자의 자연어 질문은 **Orchestrator(AI 에이전트)** 에 의해 해석되며,  
에이전트는 **[가게 프로필] 컨텍스트**를 바탕으로 가장 적절한 도구를 스스로 선택하고 실행하여 답변을 생성합니다.

```mermaid
graph TD
    A[Streamlit UI] -- 1. 가게 선택 --> B[FastAPI Server (api/server.py)];
    B -- 2. 가맹점 프로필 (Dict) --> A;
    
    A -- 3. 채팅 입력
(Query + Profile + History) --> C[Orchestrator (orchestrator.py)
AgentExecutor];
    
    C -- 4. LLM이 의도 분석 후 도구 선택 --> D{Tool Routing};
    
    D -- "축제 추천해줘" --> E[Tool: recommend_festivals
(modules/filtering.py)];
    E -- (FAISS 검색 + LLM 동적 평가) --> F[축제 Top3 List];
    
    D -- "마케팅 전략 알려줘" --> G[Tool: search_contextual_marketing_strategy
(modules/knowledge_base.py)];
    G -- (RAG 검색 + LLM 전략 생성) --> H[맞춤 전략 Text];
    
    D -- "우리 가게 분석해줘" --> I[Tool: analyze_merchant_profile
(modules/tool_definitions.py)];
    I -- (LLM SWOT 분석) --> J[가게 분석 Text];
    
    D -- "A 축제 어때?" --> K[Tool: analyze_festival_profile
(modules/tool_definitions.py)];
    K -- (LLM 축제 요약) --> L[축제 분석 Text];
    
    F --> C;
    H --> C;
    J --> C;
    L --> C;
    
    C -- 5. [도구 결과]로 최종 답변 생성 (LLM) --> A;
    A -- 6. AI 컨설팅 답변 출력 --> M[사용자];

    style A fill:#4CAF50,color:#fff
    style B fill:#FF9800,color:#fff
    style C fill:#E91E63,color:#fff
    style D fill:#9C27B0,color:#fff
    style E fill:#03A9F4,color:#fff
    style G fill:#03A9F4,color:#fff
    style I fill:#03A9F4,color:#fff
    style K fill:#03A9F4,color:#fff
```

### 📍 데이터 흐름 상세 설명

**[1-2] 프로필 로드 (UI → API → UI)**  
- 사용자가 `streamlit_app.py`에서 가게를 선택합니다.  
- Streamlit이 `api/server.py`의 `/profile` 엔드포인트를 호출하여 해당 가게의 원본 프로필 데이터를 가져옵니다.  
- 이 데이터는 세션(`st.session_state.profile_data`)에 저장됩니다.

**[3] 에이전트 호출 (UI → Orchestrator)**  
- 사용자가 채팅을 입력하면, `streamlit_app.py`는 `orchestrator.execute_plan()`을 호출합니다.  
- 이때 **① 사용자 질문(Query), ② 가게 프로필(Dict), ③ 이전 대화 기록(History)** 이 Orchestrator에게 전달됩니다.

**[4] 의도 분석 및 도구 라우팅 (Orchestrator → LLM → Tool)**  
- `orchestrator.py`는 `profile_utils.py`를 사용해 API 응답(Dict)을 ‘채팅용 프로필(JSON)’로 변환합니다.  
- LLM 기반 에이전트는 (질문 + 프로필 + 대화 기록 + 시스템 프롬프트)을 바탕으로 사용자의 의도를 분석합니다.  
- 등록된 여러 `@tool` 중 **가장 적합한 하나의 도구를 선택**하여 실행합니다.

**[5] 도구 실행 및 최종 답변 생성 (Tool → Orchestrator → LLM → UI)**  
- (도구 실행) 선택된 도구(예: `recommend_festivals`)가 실행되어 결과물(예: 축제 Top3 리스트)을 반환합니다.  
- (최종 답변 생성) Orchestrator는 이 **도구 실행 결과를 다시 LLM에 주입**하여, 사용자에게 보여줄 자연어 답변(Markdown 컨설팅 리포트)을 생성합니다.  
- (답변 출력) 최종 답변은 `streamlit_app.py`로 전달되어 채팅창에 표시됩니다.

---

## 💡 기술 스택

- **Frontend:** Streamlit  
- **Backend:** FastAPI  
- **AI Model:** Gemini 2.5 Flash  
- **AI Framework:** LangChain (Agents, Tool Calling)  
- **RAG Engine:** FAISS  
- **Embeddings:** HuggingFace `dragonkue/BGE-m3-ko`  
- **Data:** Pandas, NumPy, Matplotlib  

---

## 🚀 실행 방법

### 1️⃣ 사전 준비
- `data/final_df.csv`, `data/festival_df.csv` 확인
- `vectorstore/faiss_festival`, `vectorstore/faiss_marketing` 존재해야 함
- Google API 키 발급 및 환경변수 등록

```bash
set GOOGLE_API_KEY="발급받은_API_키"
```

### 2️⃣ 환경 설정

```bash
pip install uv
uv venv
call .venv\Scripts\activate.bat
uv pip install -r requirements.txt
```

### 3️⃣ FastAPI 서버 실행

```bash
python api/server.py
# → http://127.0.0.1:8000 에서 대기
```

### 4️⃣ Streamlit 앱 실행

```bash
streamlit run streamlit_app.py
```

---

## 📈 예시 시나리오

| 사용자 입력 | 실행 도구 | 결과 |
|--------------|------------|------|
| "우리 가게 분석해줘" | `analyze_merchant_profile` | SWOT 분석 리포트 |
| "주말 방문 고객을 늘리고 싶어요" | `recommend_festivals` | Top 3 축제 추천 |
| "서울디저트페어 마케팅 전략 알려줘" | `create_festival_specific_marketing_strategy` | 맞춤형 전략 제안 |

---

## 🧠 핵심 아이디어
> “LLM이 스스로 도구를 선택하고 실행하는 Agentic RAG”

- LangChain의 **Tool-Calling Agent** 구조로 설계  
- 가게 프로필(JSON)을 컨텍스트로 하는 자연어 질의 기반 의사결정  
- FAISS + LLM 재평가 기반 **하이브리드 축제 추천 엔진**  

---

## 🏁 License

MIT License © 2025 AI Festival Consultant Team
