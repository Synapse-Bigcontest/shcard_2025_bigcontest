import streamlit as st
import json
import pandas as pd
import altair as alt # Altair 라이브러리 임포트
from typing import Optional, Dict, Any

def create_visualization(profile_data_json: Optional[str]):
    """
    JSON 형식의 전체 분석 데이터를 받아 Streamlit에 프로파일 테이블 및 그래프 형태로 표시합니다.
    """
    if not profile_data_json:
        st.warning("표시할 가맹점 프로파일 데이터가 없습니다.")
        return

    try:
        # JSON 문자열을 파싱하여 전체 데이터를 가져옵니다.
        data: Dict[str, Any] = json.loads(profile_data_json)
    except json.JSONDecodeError:
        st.error("잘못된 JSON 형식의 데이터입니다.")
        return
        
    st.markdown("---")
    st.subheader("📊 가맹점 상세 분석 요약")

    # ----------------------------------------------------------------
    # 1. 주요 현황 요약 테이블 (테이블로 유지)
    # ----------------------------------------------------------------
    st.markdown("#### 1. 주요 현황 요약")
    
    summary_items = {
        "가맹점명": data.get("가맹점명"),
        "가맹점ID": data.get("가맹점ID"),
        "상권/업종": f"{data.get('상권', 'N/A')} / {data.get('업종', 'N/A')}",
        "주소": data.get("주소"),
        "기준년월": data.get("데이터 기준년월"),
    }
    
    # 데이터프레임으로 변환 후 Streamlit 테이블로 표시
    st.table(pd.DataFrame(list(summary_items.items()), columns=['항목', '내용']))

    # ----------------------------------------------------------------
    # 2. 고객 및 매출 분석 텍스트
    # ----------------------------------------------------------------
    st.markdown("#### 2. 고객 및 매출 분석")
    
    st.markdown(f"""
    - **월매출 수준**: **{data.get('월매출수준', 'N/A')}**
    - **주요 고객 유형**: {data.get('주요 고객 유형', 'N/A')}
    - **신규/재방문율**: {data.get('신규/재방문율', 'N/A')}
    - **상권 대비 순위**: **{data.get('상권_내_순위', 'N/A')}**
    - **업종 대비 순위**: **{data.get('업종_내_순위', 'N/A')}**
    """)

    # ----------------------------------------------------------------
    # 3. 주요 고객층 상세 비율 (막대 그래프로 변경)
    # ----------------------------------------------------------------
    vis_data = data.get('visualization_data', {})
    demographics_list = vis_data.get('customer_demographics')
    
    if demographics_list:
        st.markdown("#### 3. 👥 주요 고객층 상세 비율 (시각화)")
        df_customer = pd.DataFrame(demographics_list)
        
        # 비율이 0~1 사이의 값이므로 100을 곱하여 퍼센트로 만듭니다.
        # Altair에서 차트 생성 시 비율(%)을 사용합니다.
        df_customer['비율 (%)'] = df_customer['비율'] * 100
        
        # Altair 막대 그래프 생성
        chart = alt.Chart(df_customer).mark_bar(
            color='#FF5733', # 신한카드를 상징하는 주황/빨강 계열 색상 사용
            cornerRadiusTopLeft=3,
            cornerRadiusTopRight=3
        ).encode(
            x=alt.X('비율 (%):Q', title='매출 기여 비율 (%)'),
            y=alt.Y('고객층:N', title='고객층', sort='-x'), # 비율이 높은 순으로 정렬
            tooltip=['고객층', alt.Tooltip('비율 (%):Q', format='.1f')]
        ).properties(
            title="주요 고객층 매출 기여도"
        ).interactive() # 마우스 오버 시 상호작용 가능하도록 설정
        
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("주요 고객층 상세 데이터가 없습니다.")
