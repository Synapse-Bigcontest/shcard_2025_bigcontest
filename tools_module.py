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
    
    # ... (데이터 요약 로직은 기존과 동일)
    latest_data = filtered_df.sort_values(by='기준년월', ascending=False).iloc[0]
    
    기준년월_str = latest_data.get('기준년월', 'N/A')
    if hasattr(기준년월_str, 'strftime'):
        기준년월_str = 기준년월_str.strftime('%Y년 %m월')
    
    merchant_name = latest_data.get('가맹점명', '미확인')
    
    # LLM이 분석할 최종 요약 데이터
    summary_data = {
        "가맹점명": merchant_name,
        "가맹점ID": merchant_id,
        "상권": latest_data.get('상권', 'N/A'),
        "업종": latest_data.get('업종', 'N/A'),
        # ... (나머지 분석 데이터 포함)
        "주소": latest_data.get('가맹점주소', 'N/A'),
        "주요 고객 유형": (
            f"1. 유동인구 {latest_data.get('유동인구이용비율', 0) * 100:.1f}%, "
            f"2. 거주자 {latest_data.get('거주자이용비율', 0) * 100:.1f}%, "
            f"3. 직장인 {latest_data.get('직장인이용비율', 0) * 100:.1f}%"
        ),
        "주요 고객층 비율 (LLM 분석용)": {
            "여성_20대": latest_data.get('여성20대이하비율', 0),
            "남성_20대": latest_data.get('남성20대이하비율', 0),
            "여성_30대": latest_data.get('여성30대비율', 0),
            "남성_30대": latest_data.get('남성30대비율', 0),
        },
        "신규/재방문율": (
            f"신규 {latest_data.get('신규고객비율', 0) * 100:.1f}% "
            f"재방문 {latest_data.get('재이용고객비율', 0) * 100:.1f}%"
        ),
        "월매출수준": latest_data.get('월매출금액_구간', '미측정'),
        "배달매출비율": f"{latest_data.get('배달매출비율', 0) * 100:.1f}%",
        "동일 상권 대비 매출 순위": f"상위 {latest_data.get('동일상권내매출순위비율', 0) * 100:.1f}%",
        "동일 업종 대비 매출 순위": f"상위 {latest_data.get('동일업종내매출순위비율', 0) * 100:.1f}%",
        "데이터 기준년월": 기준년월_str
    }

    summary_json = json.dumps(summary_data, indent=2, ensure_ascii=False)
    
    return {
        "found": True,
        "message": f"가맹점명 '{merchant_name}' (ID: {merchant_id})에 대한 핵심 요약 데이터입니다. 아래 JSON을 참조하여 요청하신 형식의 표를 만드세요.",
        "count": 1,
        "merchant_name": merchant_name, 
        "analysis_data": summary_json
    }

# ⭐️ TOOLS 목록 업데이트: 이제 분석 툴만 포함합니다.
TOOLS = [analyze_merchant_data]