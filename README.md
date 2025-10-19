# 🎈 AI 축제 컨설턴트

> **Agentic RAG 기반 소상공인 맞춤형 지역 축제 컨설팅 시스템**

신한카드 빅데이터와 전국 축제 정보를 통합 분석하여,  
AI가 **가게별로 참여할 만한 지역 축제**와 **최적의 마케팅 전략 보고서**를 자동 생성합니다.

---

## 🧭 프로젝트 개요

이 프로젝트는 **Streamlit 웹 인터페이스 + FastAPI 서버 + LangChain 기반 Orchestrator**로 구성된  
**AI 컨설팅 자동화 시스템**입니다.

사용자는 자신의 가게를 선택하고 “어떤 고객층을 늘리고 싶다” 등의 질문을 입력하면,  
AI가 다음을 자동 수행합니다:

1. 가맹점 데이터 분석 (FastAPI)
2. 축제 추천 (FAISS + LLM 하이브리드)
3. 마케팅 전략 RAG 검색
4. 자연어 기반 컨설팅 보고서 생성

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
│   ├── data_loader.py        # 데이터 로드 및 전처리
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
    ├── faiss_festivals       # 축데 데이터 저장소
    └── faiss_marketing       # 마케팅 전략 데이터 저장소
```

---

## ⚙️ 주요 기능 요약

| 구분 | 파일 | 주요 기능 |
|------|-------|------------|
| **데이터 로드** | `api/data_loader.py` | CSV 안전 로드 및 전처리 |
| **API 서버** | `api/server.py` | FastAPI 기반 가맹점 프로필 API |
| **AI 오케스트레이션** | `orchestrator.py` | 전체 파이프라인 실행 중심 |
| **RAG / 벡터검색** | `modules/knowledge_base.py` | 축제/마케팅 FAISS 인덱스 로드 |
| **축제 추천 엔진** | `modules/filtering.py` | LLM + FAISS 하이브리드 추천 |
| **보고서 생성기** | `modules/generation.py` | 맞춤형 컨설팅 보고서 생성 |
| **시각화 모듈** | `modules/visualization.py` | Streamlit 시각화 컴포넌트 |
| **UI** | `streamlit_app.py` | Streamlit 프론트엔드 |
| **LangChain Tools** | `modules/tool_definitions.py` | Tool 정의 및 연결 |

---

## 🔄 전체 데이터 흐름

```text
Streamlit UI (사장님 질문 입력)
        ↓
[1] get_merchant_profile()  
 └─ (FastAPI: api/server.py) → 가게 프로필 획득
        ↓
[2] filtering.run_festival_recommendation()
 ├─ (LLM 1) 쿼리 재작성 (프로필 + 질문)
 ├─ (FAISS) 축제 후보군 검색 (Top N)
 ├─ (LLM 2) 동적 채점 기준 생성
 ├─ (LLM 3) 후보군 일괄 평가 (Batch re-ranking)
 └─ (Hybrid) 벡터 유사도 + LLM 평가 결합 → Top 3 선정
        ↓
[3] knowledge_base.search_contextual_marketing_strategy()
 └─ (RAG) 마케팅 DB 검색 → 맞춤 전략 확보
        ↓
[4] generation.format_final_response()
 └─ (LLM 4) 최종 Markdown 컨설팅 보고서 생성
        ↓
Streamlit UI (보고서 출력)
```

---

## 🧾 상세 코드 설명

#### 1) Frontend (UI) — `streamlit_app.py`
- Streamlit 기반 인터페이스로 사용자가 가게 선택, 질문 입력, 보고서 열람을 수행합니다.
- 앱 초기화 시 `modules/knowledge_base.py`로 RAG용 벡터 DB를 로드하고 Orchestrator를 초기화합니다.
- `visualization.py`를 호출해 가맹점 성과, 고객 분포 등 시각화를 제공합니다.

#### 2) Backend (Data API) — `api/server.py`, `api/data_loader.py`
- `server.py`: `/profile` 엔드포인트 구현. `merchant_id`로 `final_df.csv`에서 최신 프로필과 상권 평균을 반환합니다.
- `data_loader.py`: 데이터 로드·클리닝·타입 정리 및 캐시 로직(필요 시)을 포함합니다.

#### 3) AI Orchestrator — `orchestrator.py`
- LangChain 기반 Orchestrator가 LLM과 Tool(데이터 API, RAG 등)을 연결해 파이프라인을 실행합니다.
- 주요 함수:
  - `get_store_profile_only()` — 가게 프로필 조회 도구 호출
  - `execute_plan(user_query, merchant_id)` — 전체 실행 흐름(프로필 → 필터링 → RAG → 리포트)

#### 4) Knowledge Base & RAG — `knowledge_base.py`
- FAISS 인덱스(축제용, 마케팅용)를 로드하고 각 인덱스에 맞는 retriever를 제공합니다.
- `search_contextual_marketing_strategy(profile, query)` 같은 도구 함수를 통해 RAG 검색 결과를 반환합니다.

#### 5) Advanced Filtering Engine — `filtering.py`
- 하이브리드 추천 파이프라인 (요약):
  1. `rewrite_query_with_llm(profile, query)` — 의미 검색용 쿼리 생성 (LLM)
  2. `search_faiss_candidates(query_embedding, top_k)` — 후보군 추출
  3. `create_dynamic_scoring_criteria(profile, query)` — 동적 채점 기준 생성 (LLM)
  4. `evaluate_candidates_in_batch(candidates, criteria)` — 후보 일괄 평가 (LLM)
  5. `calculate_hybrid_scores(vec_scores, llm_scores, weights)` — 하이브리드 점수 계산 및 정렬

#### 6) Final Report Generator — `generation.py`
- `format_final_response(context)`가 LLM을 호출해 최종 Markdown 리포트를 생성합니다. 리포트 구성: 인사말, 추천 축제 Top3, 채점 근거, 마케팅 전략, 실행 제안(체크리스트) 등.

#### 7) Tools & Visualization
- `modules/tool_definitions.py`에 Orchestrator가 호출할 수 있는 도구들을 정의합니다 (예: `get_merchant_profile()`, `get_festival_info()` 등).
- `visualization.py`는 Matplotlib 기반 차트를 만들고 Streamlit에 렌더링합니다(차트는 재사용 가능한 함수로 구성).

---

## 💡 주요 기술 스택

- **Frontend:** Streamlit (Python UI)
- **Backend:** FastAPI (REST API)
- **AI Model:** Gemini 2.5 Flash (Google Generative AI)
- **RAG Engine:** LangChain + FAISS + HuggingFace Embeddings(dragonkue/BGE-m3-ko)
- **Data Analysis:** Pandas, NumPy, Matplotlib

---

## 🚀 실행 방법

### 1️⃣ FastAPI 서버 실행
```bash
cd C:\(다운받은 폴더 위치)
uv venv
call .venv\Scripts\activate.bat
uv pip install -r requirements.txt
python api/server.py
```

### 2️⃣ Streamlit 앱 실행
```bash
cd C:\(다운받은 폴더 위치)
uv venv
call .venv\Scripts\activate.bat
uv pip install -r requirements.txt
mkdir .streamlit
echo GOOGLE_API_KEY="(발급받은 API key)" > .streamlit\secrets.toml
uv run streamlit run streamlit_app.py
```

---

## 📈 결과 예시

- Streamlit에서 가게 선택 → AI 컨설턴트와 실시간 상담
- 축제 Top 3 + 채점 근거 + 마케팅 전략 자동 생성
- Markdown 형식의 완전한 컨설팅 리포트 출력

---

## 📈 사용 시나리오 예
1. 점주: “주말 방문 고객을 늘리고 싶어요(20대 여성 중심)” → AI가 디저트·핸드메이드 축제 Top3와 타겟별 마케팅 메시지 제공
2. 점주: “야간 행사에 참여하면 어떤 장점이 있나요?” → 야간 축제 추천 + 유동인구·매출 시뮬레이션(간단 표) 제공

---
