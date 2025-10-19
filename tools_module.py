# tools_module.py

from langchain.tools import tool
from typing import Dict, Any
import json
import pandas as pd

try:
    # data_processor.py에서 캐싱된 통합 데이터프레임 임포트
    from data_processor import DF_MERGED
except ImportError:
    DF_MERGED = pd.DataFrame()

# ----------------------------------------------------
# ⭐️ (참고용으로 남겨둠: 이제 Agent의 TOOL 목록에는 포함되지 않음) ⭐️
# ----------------------------------------------------
@tool
def search_merchant_id_by_name(partial_name: str) -> Dict[str, Any]:
    """
    가맹점명의 일부 문자열을 입력받아, 해당하는 가맹점 ID 목록을 검색합니다. 
    (참고: 이 툴은 현재 ID 분석 모드에서는 사용되지 않습니다.)
    """
    if DF_MERGED.empty:
        return {"found": False, "message": "데이터프레임이 로드되지 않았습니다."}
    
    df_temp = DF_MERGED.reset_index()
    search_term = partial_name.strip()
    
    # ... (검색 로직 생략)
    
    return {
        "found": False, # 분석 모드에서는 사용하지 않음을 명시
        "message": f"현재는 ID 분석 모드입니다. 가맹점 ID를 직접 입력해주세요."
    }


# ----------------------------------------------------
# ⭐️ 툴 2: 가맹점 ID를 입력받아 데이터를 분석하는 툴 ⭐️
# ----------------------------------------------------
@tool
def analyze_merchant_data(merchant_id: str) -> Dict[str, Any]:
    """
    가맹점 ID를 입력받아 해당 가맹점의 핵심 요약 정보를 검색하고 LLM 분석을 위한 JSON 데이터를 반환합니다.
    """
    if DF_MERGED.empty:
        return {"found": False, "message": "데이터프레임이 로드되지 않았습니다.", "count": 0, "merchant_name": None}
    
    # 인덱스 기반 검색
    try:
        # DF_MERGED는 가맹점ID가 인덱스이므로 loc 사용
        filtered_df = DF_MERGED.loc[[merchant_id]].copy()
    except KeyError:
        return {"found": False, "message": f"가맹점ID '{merchant_id}'에 해당하는 정확한 데이터를 찾을 수 없습니다. ID를 확인해주세요.", "count": 0, "merchant_name": None}
    
    if filtered_df.empty:
        return {"found": False, "message": f"가맹점ID '{merchant_id}'에 해당하는 데이터가 없습니다.", "count": 0, "merchant_name": None}

    # 최신 데이터 추출
    latest_data = filtered_df.sort_values(by='기준년월', ascending=False).iloc[0]
    
    # 데이터 형식 변환 (기준년월)
    기준년월_str = latest_data.get('기준년월', 'N/A')
    if hasattr(기준년월_str, 'strftime'):
        기준년월_str = 기준년월_str.strftime('%Y년 %m월')
    
    merchant_name = latest_data.get('가맹점명', '미확인')

    # ----------------------------------------------------------------------
    # ⭐️ 1. 시각화 모듈용 데이터 준비 (상세 고객층 비율) ⭐️
    # ----------------------------------------------------------------------
    
    # DF_MERGED에는 '여성20대이하비율', '남성20대이하비율' 등의 컬럼이 포함되어 있다고 가정합니다.
    gender_age_cols = [col for col in filtered_df.columns if ('여성' in col or '남성' in col) and '비율' in col]
    gender_age_means = latest_data[gender_age_cols]
    
    # 상위 6개 고객층 추출
    customer_demographics_data = gender_age_means.sort_values(ascending=False).head(6).reset_index().rename(columns={'index': '고객층', merchant_id: '비율'})
    # 비율 데이터를 딕셔너리 리스트로 변환 (시각화 모듈에서 사용)
    customer_demographics_list = customer_demographics_data.to_dict('records')
    
    # ----------------------------------------------------------------------
    # ⭐️ 2. LLM이 분석할 최종 요약 데이터 구성 (이전 코드 + 시각화 데이터 통합) ⭐️
    # ----------------------------------------------------------------------

    # tools_module의 키와 visualization.py의 키를 맞추기 위해 일부 키를 재정의하거나 추가합니다.
    
    # 순위 지표 (전처리됨)
    # LLM용 키를 visualization.py에서 사용하는 키로 변경/정의합니다.
    # LLM이 사용할 상권/업종 순위 (예: 0.8 -> 상위 80.0%)
    same_area_rank_pct = latest_data.get('상권내_매출순위', 0.5) 
    same_ind_rank_pct = latest_data.get('업종내_매출순위', 0.5)

    # %로 변환된 상위 순위 (사용자 친화적)
    top_area_rank = 100 - same_area_rank_pct * 100
    top_ind_rank = 100 - same_ind_rank_pct * 100

    # 고객 지표
    re_use_pct = latest_data.get('재이용고객비율', 0)
    new_cust_pct = latest_data.get('신규고객비율', 0)

    summary_data = {
        # ⭐️ LLM과 Visualization 공통 사용 데이터 (최상위 레벨) ⭐️
        "가맹점명": merchant_name,
        "가맹점ID": merchant_id,
        "상권": latest_data.get('상권', 'N/A'),
        "업종": latest_data.get('업종', 'N/A'),
        "주소": latest_data.get('가맹점주소', 'N/A'),
        "데이터 기준년월": 기준년월_str, # visualization.py에서 '기준년월' 키 대신 '데이터 기준' 키를 사용하도록 수정 필요
        
        # ⭐️ LLM 응답/Visualization 텍스트 요약용 데이터 ⭐️
        "주요 고객 유형": (
            f"1. 유동인구 {latest_data.get('유동인구이용비율', 0) * 100:.1f}%, "
            f"2. 거주자 {latest_data.get('거주자이용비율', 0) * 100:.1f}%, "
            f"3. 직장인 {latest_data.get('직장인이용비율', 0) * 100:.1f}%"
        ),
        "신규/재방문율": (
            f"신규 {new_cust_pct * 100:.1f}% / "
            f"재방문 {re_use_pct * 100:.1f}%"
        ),
        "월매출수준": latest_data.get('월매출금액_구간', '미측정'), # 예: '1_10%이하'
        # Visualization.py에서 사용할 키로 통일 (순위)
        "상권_내_순위": f"상위 {top_area_rank:.1f}%",
        "업종_내_순위": f"상위 {top_ind_rank:.1f}%",
        
        # ⭐️ Visualization.py가 테이블을 만들 때 사용할 상세 데이터 ⭐️
        "visualization_data": {
            "customer_demographics": customer_demographics_list, # 상위 6개 상세 비율
        },
        
        # ⭐️ 기존 LLM 분석용 데이터를 유지하기 위한 키 (필요 시 유지) ⭐️
        "주요 고객층 비율 (LLM 분석용)": {
            "여성_20대": latest_data.get('여성20대이하비율', 0),
            "남성_20대": latest_data.get('남성20대이하비율', 0),
            "여성_30대": latest_data.get('여성30대비율', 0),
            "남성_30대": latest_data.get('남성30대비율', 0),
        },
    }

    summary_json = json.dumps(summary_data, indent=2, ensure_ascii=False)
    
    return {
        "found": True,
        "message": f"가맹점명 '{merchant_name}' (ID: {merchant_id})에 대한 핵심 요약 데이터 및 **시각화용 데이터**입니다. [LLM에게 경고: JSON은 사용자에게 절대 보여주지 마세요.]",
        "count": 1,
        "merchant_name": merchant_name, 
        "analysis_data": summary_json # 전체 요약 및 시각화 데이터를 포함하는 JSON 문자열
    }

# ⭐️ TOOLS 목록 업데이트: 이제 분석 툴만 포함합니다.
TOOLS = [analyze_merchant_data]