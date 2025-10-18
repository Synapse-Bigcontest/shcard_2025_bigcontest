# modules/visualization.py

import streamlit as st
import json
import pandas as pd
from typing import Optional

def display_merchant_profile(profile_data_json: Optional[str]):
    """
    JSON 형식의 가맹점 프로파일 데이터를 받아 Streamlit에 표시합니다.
    (이 함수는 현재 챗봇 모드에서 LLM이 표를 직접 생성하므로 사용하지 않을 수 있지만, 구조를 위해 유지합니다.)
    """
    if not profile_data_json:
        st.warning("표시할 가맹점 프로파일 데이터가 없습니다.")
        return

    try:
        data = json.loads(profile_data_json)
    except json.JSONDecodeError:
        st.error("잘못된 JSON 형식의 데이터입니다.")
        return

    st.markdown("#### 1. 주요 현황 요약")
    
    summary_items = {
        "가맹점명": data.get("가맹점명"),
        "가맹점ID": data.get("가맹점ID"),
        "상권/업종": f"{data.get('상권')} / {data.get('업종')}",
        "주소": data.get("주소"),
        "데이터 기준": data.get("데이터 기준년월"),
    }
    st.table(pd.DataFrame(list(summary_items.items()), columns=['항목', '내용']))

    st.markdown("#### 2. 고객 및 매출 분석")
    
    st.markdown(f"""
    - **주요 고객 유형**: {data.get('주요 고객 유형')}
    - **신규/재방문율**: {data.get('신규/재방문율')}
    - **월매출 수준**: {data.get('월매출수준')}
    - **배달 매출 비율**: {data.get('배달매출비율')}
    - **상권 대비 순위**: {data.get('동일 상권 대비 매출 순위')}
    - **업종 대비 순위**: {data.get('동일 업종 대비 매출 순위')}
    """)

    if '주요 고객층 비율 (LLM 분석용)' in data:
        st.markdown("##### 주요 고객층 상세 비율 (LLM 분석용)")
        df_customer = pd.DataFrame(data['주요 고객층 비율 (LLM 분석용)'].items(), columns=['고객층', '비율'])
        df_customer['비율'] = (df_customer['비율'] * 100).round(1).astype(str) + '%'
        st.dataframe(df_customer, hide_index=True, use_container_width=True)