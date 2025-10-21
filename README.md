# 🎈 AI 축제 컨설턴트 (Agentic RAG)

## Agentic RAG 기반 소상공인 맞춤형 지역 축제 컨설팅 시스템
## 저녁쯤에 수정된 축제 데이터 받아서 아직 축제 추천 방법 수정 X

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

## ⚙️ 주요 기능 요약

| 구분 | 파일 | 주요 기능 |
|------|------|------------|
| 데이터 로드 | `api/data_loader.py` | CSV 로드 및 전처리 |
| API 서버 | `api/server.py` | `/profile` 엔드포인트 제공 |
| AI 에이전트 | `orchestrator.py` | LLM 기반 도구 선택 및 실행 |
| RAG | `knowledge_base.py` | FAISS 벡터 스토어 + HuggingFace 임베딩 |
| 축제 추천 | `filtering.py` | FAISS + LLM 하이브리드 추천 |
| 기타 도구 | `tool_definitions.py` | SWOT 분석, 축제 요약 등 |
| 프로필 표준화 | `profile_utils.py` | 에이전트용 JSON 변환 |
| 시각화 | `visualization.py` | Streamlit 그래프 생성 |
| LLM 관리 | `llm_provider.py` | Gemini LLM 인스턴스 재사용 |

---

## 🔄 아키텍처 및 데이터 흐름

![Architecture Diagram](https://github.com/yourname/AI_FESTIVAL_CONSULTANT/assets/architecture_diagram.png)

> 새로운 구조는 “에이전트 중심 도구 호출” 패턴을 따릅니다.

1️⃣ **프로필 로드** (UI → API)  
Streamlit 앱이 FastAPI를 호출해 가게 프로필을 로드합니다.

2️⃣ **에이전트 호출** (UI → Orchestrator)  
사용자 입력 + 프로필 + 대화 이력을 에이전트로 전달합니다.

3️⃣ **도구 라우팅** (Orchestrator → LLM)  
LLM이 적절한 도구(`@tool`)를 선택합니다.

4️⃣ **도구 실행 → 답변 생성 → UI 출력**  

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

