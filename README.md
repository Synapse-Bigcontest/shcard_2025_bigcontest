# 🎈 신한카드 AI 축제 컨설턴트

Agentic RAG 기반으로 **소상공인을 위한 맞춤형 지역 축제 부스 참여 컨설팅**을 제공하는 AI 시스템입니다.  
신한카드 빅데이터, 축제 정보, 날씨 데이터를 통합 분석하여, AI가 자율적으로 상권별 맞춤 축제를 추천하고
최적의 마케팅 전략 보고서를 생성합니다.

---

## 🧭 프로젝트 개요

이 프로젝트는 Streamlit 기반 웹 인터페이스와 FastAPI 서버, LangChain 기반 Agent Orchestrator로 구성된
**AI 컨설팅 자동화 시스템**입니다.  
사용자는 가게를 선택하고, AI에게 “어떤 고객을 늘리고 싶다” 등의 질문을 하면
AI가 빅데이터 분석 결과를 바탕으로 **가게 특성에 맞는 축제 및 마케팅 전략을 제안**합니다.

---

## 📂 프로젝트 구조

```
AI_FESTIVAL_CONSULTANT/
├── orchestrator.py           # AI 에이전트 실행 및 도구 호출 관리 (메인 엔진)
├── streamlit_app.py          # Streamlit 웹 인터페이스 (UI)
│
├── api/
│   ├── server.py             # FastAPI 기반 데이터 조회 서버
│   └── data_loader.py        # 데이터 로드 및 전처리
│
├── modules/
│   ├── knowledge_base.py     # RAG 및 벡터 스토어 로더
│   ├── tool_definitions.py   # LangChain Tool 정의 (가맹점, 축제 정보)
│   ├── filtering.py          # 축제 추천 파이프라인 (LLM + FAISS)
│   ├── generation.py         # 최종 컨설팅 보고서 생성
│   └── visualization.py      # Streamlit 시각화 (가맹점 분석 그래프)
│
└── data/
│   ├── final_df.csv          # 가맹점 데이터
│   └── festival_df.csv       # 축제 정보 데이터
│
└── vectorstore/              # FAISS 인덱스 저장소
│   ├── faiss_festivals       # 축제 데이터 인덱스 
│   └── faiss_marketing       # 마케팅 전략 인덱스
```

---

## ⚙️ 주요 기능 요약

| 구분 | 파일 | 주요 기능 |
|------|-------|------------|
| 데이터 로드 | `data_loader.py` | CSV 안전 로드 및 전처리 |
| API 서버 | `server.py` | FastAPI 기반 가맹점 프로필 API |
| AI 오케스트레이션 | `orchestrator.py` | 전체 파이프라인 실행 중심 |
| 벡터/RAG | `knowledge_base.py` | FAISS 인덱스 + 마케팅 전략 RAG |
| 축제추천엔진 | `filtering.py` | LLM+FAISS 기반 추천 파이프라인 |
| 보고서 생성 | `generation.py` | LLM으로 자연어 보고서 생성 |
| 시각화 | `visualization.py` | Streamlit 그래프 및 표 렌더링 |
| 웹 인터페이스 | `streamlit_app.py` | Streamlit 전체 UI/UX 구성 |
| 도구정의 | `tool_definitions.py` | LangChain Tool 정의(API, 축제정보 등) |

---

## 🔄 전체 데이터·처리 흐름

```
Streamlit UI
   ↓
Orchestrator (execute_plan)
   ├─ get_merchant_profile (FastAPI 서버 호출)
   ├─ filtering.run_festival_recommendation()
   │     ├─ query rewrite → FAISS 검색 → LLM 평가 → hybrid score 계산
   │     └─ 축제 Top3 추천
   ├─ knowledge_base.search_contextual_marketing_strategy()
   └─ generation.format_final_response()
          ↓
  Markdown 형식 컨설팅 보고서 출력
```

---

## 💡 주요 기술 스택

- **Frontend:** Streamlit (Python UI)
- **Backend:** FastAPI (REST API)
- **AI Model:** Gemini 2.5 Flash (Google Generative AI)
- **RAG Engine:** LangChain + FAISS + HuggingFace Embeddings
- **Data Analysis:** Pandas, NumPy, Matplotlib

---

## 🚀 실행 방법
### 1️⃣ FastAPI 서버 실행
```bash
cd C:\(저장한 폴더 위치)
uv venv
call .venv\Scripts\activate.bat
uv pip install -r requirements.txt
python api/server.py
```

### 2️⃣ Streamlit 앱 실행
```bash
cd C:\(저장한 폴더 위치)
uv venv
call .venv\Scripts\activate.bat
uv pip install -r requirements.txt
mkdir .streamlit
echo GOOGLE_API_KEY="(발급받은 api key)" > .streamlit\secrets.toml
uv run streamlit run streamlit_app.py
```

---

## 📈 결과 예시

- Streamlit에서 가게 선택 → AI 컨설턴트와 실시간 상담
- 축제 Top 3 + 채점 근거 + 마케팅 전략 자동 생성
- Markdown 형식의 완전한 컨설팅 리포트 출력

