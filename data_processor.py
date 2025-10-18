# data_processor.py (Streamlit App용 Data Layer)

import pandas as pd
import streamlit as st
import os

# ⭐️ 주의: 'data_processor.csv' 파일이 'data' 폴더에 생성되어 있어야 합니다. ⭐️
DATA_FILE_NAME = "data_processor.csv"

# Streamlit 앱 실행 위치를 기준으로 'data' 폴더 내의 파일 경로를 지정합니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_dir, 'data')
FILE_PATH = os.path.join(data_dir, DATA_FILE_NAME)


@st.cache_data(show_spinner="대용량 데이터 로드 및 인덱싱 중...")
def load_and_preprocess_data() -> pd.DataFrame:
    """
    미리 전처리된 최종 CSV 파일을 로드하고 '가맹점ID'를 인덱싱하여 DF_MERGED를 생성합니다.
    """
    try:
        if not os.path.exists(FILE_PATH):
            st.error(f"❌ '{DATA_FILE_NAME}' 파일이 경로에 없습니다. 'preprocess_data.py'를 먼저 실행하여 파일을 생성하세요!")
            return pd.DataFrame()
            
        # 전처리된 최종 CSV 파일 로드 (이미 한글 컬럼명)
        df_merged = pd.read_csv(FILE_PATH, encoding="utf-8-sig")
        
        # ⭐️ 로드 후 다시 형식 변환 및 최적화
        df_merged['기준년월'] = pd.to_datetime(df_merged['기준년월']) 
        df_merged['가맹점ID'] = df_merged['가맹점ID'].astype(str)
        
        # ⭐️⭐️⭐️ 최적화: '가맹점ID'를 인덱스로 설정 ⭐️⭐️⭐️
        df_merged.set_index('가맹점ID', inplace=True)
        
        return df_merged
        
    except Exception as e:
        st.error(f"❌ data_processor.py: 데이터 로드 중 예상치 못한 오류 발생: {e}")
        return pd.DataFrame()

# 전체 어플리케이션에서 사용할 통합 데이터프레임
DF_MERGED: pd.DataFrame = load_and_preprocess_data()