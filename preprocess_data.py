# preprocess_data.py

import pandas as pd
import numpy as np
import os
import sys

# --------------------------------------------------------------------------
# 초기 설정: 경로 및 파일명 정의
# --------------------------------------------------------------------------

# 스크립트 파일이 위치한 디렉토리를 기준으로 경로 설정
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, 'data')

if not os.path.exists(data_dir):
    print(f"Error: Data directory not found at {data_dir}. Please create a 'data' folder and place CSV files inside.")
    sys.exit(1)

def get_file_path(filename):
    """data 폴더 내의 파일 경로를 반환합니다."""
    return os.path.join(data_dir, filename)

# --------------------------------------------------------------------------
# 1) 데이터 1 - 가맹점 개요정보 로드 및 전처리
# --------------------------------------------------------------------------

file_path1 = get_file_path('big_data_set1_f.csv')
print(f"Loading data from {file_path1}")

try:
    df1 = pd.read_csv(file_path1, encoding="cp949")
except FileNotFoundError:
    print(f"Error: File not found at {file_path1}.")
    sys.exit(1)

col_map1 = {
    "ENCODED_MCT": "가맹점ID", "MCT_BSE_AR": "가맹점주소", "MCT_NM": "가맹점명",
    "MCT_BRD_NUM": "브랜드구분코드", "MCT_SIGUNGU_NM": "지역명", "HPSN_MCT_ZCD_NM": "업종",
    "HPSN_MCT_BZN_CD_NM": "상권", "ARE_D": "개설일", "MCT_ME_D": "폐업여부"
}
df1 = df1.rename(columns=col_map1)

# - 전처리
df1['브랜드구분코드'] = df1['브랜드구분코드'].fillna('미확인')
df1['상권'] = df1['상권'].fillna('미확인')

df1['개설일'] = df1['개설일'].astype(str)
df1['개설일'] = pd.to_datetime(df1['개설일'], format='%Y%m%d', errors='coerce') 

df1['폐업여부'] = df1['폐업여부'].apply(
    lambda x: pd.to_datetime(int(x), format='%Y%m%d', errors='coerce') 
    if pd.notna(x) and str(x).isdigit() else pd.NaT
)
df1['운영상태'] = df1['폐업여부'].apply(lambda x: '운영중' if pd.isna(x) else '폐업')


# --------------------------------------------------------------------------
# 2) 데이터 2 - 가맹점 월별 이용정보 로드 및 전처리
# --------------------------------------------------------------------------

file_path2 = get_file_path('big_data_set2_f.csv')
print(f"Loading data from {file_path2}")

try:
    df2 = pd.read_csv(file_path2, encoding="cp949")
except FileNotFoundError:
    print(f"Error: File not found at {file_path2}.")
    sys.exit(1)

col_map2 = {
    "ENCODED_MCT": "가맹점ID", "TA_YM": "기준년월", "MCT_OPE_MS_CN": "운영개월수_구간",
    "RC_M1_SAA": "월매출금액_구간", "RC_M1_TO_UE_CT": "월매출건수_구간", "RC_M1_UE_CUS_CN": "월유니크고객수_구간",
    "RC_M1_AV_NP_AT": "월객단가_구간", "APV_CE_RAT": "취소율_구간", "DLV_SAA_RAT": "배달매출비율",
    "M1_SME_RY_SAA_RAT": "동일업종매출대비비율", "M1_SME_RY_CNT_RAT": "동일업종건수대비비율",
    "M12_SME_RY_SAA_PCE_RT": "동일업종내매출순위비율", "M12_SME_BZN_SAA_PCE_RT": "동일상권내매출순위비율",
    "M12_SME_RY_ME_MCT_RAT": "동일업종해지가맹점비중", "M12_SME_BZN_ME_MCT_RAT": "동일상권해지가맹점비중"
}
df2 = df2.rename(columns=col_map2)

# - 전처리
df2['기준년월'] = pd.to_datetime(df2['기준년월'].astype(str), format='%Y%m')
df2.replace(-999999.9, np.nan, inplace=True)


# --------------------------------------------------------------------------
# 3) 데이터 3 - 가맹점 월별 이용 고객정보 로드 및 전처리
# --------------------------------------------------------------------------

file_path3 = get_file_path('big_data_set3_f.csv')
print(f"Loading data from {file_path3}")

try:
    df3 = pd.read_csv(file_path3, encoding="cp949")
except FileNotFoundError:
    print(f"Error: File not found at {file_path3}.")
    sys.exit(1)

col_map3 = {
    "ENCODED_MCT": "가맹점ID", "TA_YM": "기준년월", 
    "M12_MAL_1020_RAT": "남성20대이하비율", "M12_MAL_30_RAT": "남성30대비율",
    "M12_MAL_40_RAT": "남성40대비율", "M12_MAL_50_RAT": "남성50대비율",
    "M12_MAL_60_RAT": "남성60대이상비율", "M12_FME_1020_RAT": "여성20대이하비율",
    "M12_FME_30_RAT": "여성30대비율", "M12_FME_40_RAT": "여성40대비율",
    "M12_FME_50_RAT": "여성50대비율", "M12_FME_60_RAT": "여성60대이상비율",
    "MCT_UE_CLN_REU_RAT": "재이용고객비율", "MCT_UE_CLN_NEW_RAT": "신규고객비율",
    "RC_M1_SHC_RSD_UE_CLN_RAT": "거주자이용비율", "RC_M1_SHC_WP_UE_CLN_RAT": "직장인이용비율",
    "RC_M1_SHC_FLP_UE_CLN_RAT": "유동인구이용비율"
}
df3 = df3.rename(columns=col_map3)

# - 전처리
df3['기준년월'] = pd.to_datetime(df3['기준년월'].astype(str), format='%Y%m')
df3.replace(-999999.9, np.nan, inplace=True)


# --------------------------------------------------------------------------
# 4) 데이터 통합 및 이상값 처리
# --------------------------------------------------------------------------

print("Merging dataframes...")
df23 = pd.merge(df2, df3, on=["가맹점ID", "기준년월"], how="inner")
final_df = pd.merge(df23, df1, on="가맹점ID", how="left")

# 이상값 처리 로직 (성동구 외 지역 라벨 교정)
non_seongdong_areas = [
    '압구정로데오', '풍산지구', '미아사거리', '방배역',
    '자양', '동대문역사문화공원역', '건대입구',
    '서면역', '오남'
]

mask_seongdong_addr = final_df['가맹점주소'].str.contains('성동구', na=False)
seongdong_df = final_df[mask_seongdong_addr].copy()

mask_mislabel = seongdong_df['상권'].isin(non_seongdong_areas)
seongdong_df.loc[mask_mislabel, '상권'] = '미확인(성동구)'

final_clean_df = seongdong_df[
    ~(
        (seongdong_df['상권'].str.contains('미확인')) &
        (~seongdong_df['가맹점주소'].str.contains('성동구', na=False))
    )
].copy()

# 업종 - 한 업종이 100퍼인 경우 제외(이상치 취급)
final_clean_df = final_clean_df[final_clean_df['업종'] != '유제품'].copy()


# --------------------------------------------------------------------------
# 최종 CSV 파일 저장
# --------------------------------------------------------------------------

save_path = get_file_path("data_processor.csv")

# CSV 파일 저장 (인덱스 제외)
final_clean_df.to_csv(save_path, index=False, encoding="utf-8-sig")

print(f"\n✅ 최종 전처리 및 CSV 파일 저장 완료: {save_path}")