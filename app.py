import os
import cv2
import base64
import pandas as pd
import streamlit as st
from datetime import datetime
from random import randint
from PIL import Image

# 폴더 생성
IMAGE_FOLDER = "images"
os.makedirs(IMAGE_FOLDER, exist_ok=True)

NONE = '행동 없음'
BEHAVIORS = [
    "BODYLOWER", "BODYSCRATCH", "BODYSHAKE", "FEETUP", "FOOTUP",
    "HEADING", "LYING", "MOUNTING", "SIT", "TAILING",
    "TAILLOW", "TURN", "WALKRUN"
]

def get_image_base64(image_path):
    """이미지를 base64로 인코딩"""
    with open(image_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode()
        return f"data:image/jpeg;base64,{encoded_string}"

def capture_image():
    """웹캠에서 이미지를 캡처하고 images 폴더에 저장"""
    cap = cv2.VideoCapture(0)  # 웹캠 열기
    ret, frame = cap.read()  # 한 프레임 캡처
    cap.release()  # 웹캠 해제

    if ret:
        filename = f"{IMAGE_FOLDER}/capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(filename, frame)  # 이미지 저장
        return filename
    else:
        st.error("📷 캡처 실패! 웹캠을 확인하세요.")
        return None

def get_row(time: datetime, behavior: str, image_path: str):
    """데이터프레임에 새로운 행 추가"""
    return pd.DataFrame({
        '날짜': [time.strftime('%Y-%m-%d')],
        '시간': [time.strftime('%H:%M:%S')],
        '행동': [behavior],
        '캡쳐': [get_image_base64(image_path)]
    })

# 세션 데이터 초기화
if 'log' not in st.session_state:
    st.session_state['log'] = pd.DataFrame(columns=['날짜', '시간', '행동', '캡쳐'])
if 'noti' not in st.session_state:
    st.session_state['noti'] = []
if 'behavior' not in st.session_state:
    st.session_state['behavior'] = NONE
if 'search_filter' not in st.session_state:
    st.session_state['search_filter'] = []

# 메인 UI
st.set_page_config(layout="wide")
    
tab_overview, tab_logs, tab_noti = st.tabs(['🔴 실시간 영상', '📋 전체 활동 기록',  '🔔 알림 설정'])

with tab_overview:
    col1, col2 = st.columns([25, 10], vertical_alignment='top')
    with col1:
        st.image(image='강아지3.jpg', use_column_width=True)
    with col2:
        st.markdown('### 최근에 감지된 활동')
        st.dataframe(
            st.session_state['log'].head(10),
            column_config={
                "날짜": st.column_config.TextColumn("날짜"),
                "시간": st.column_config.TextColumn("시간"),
                "행동": st.column_config.TextColumn("행동"),
                "캡쳐": st.column_config.ImageColumn(
                    "캡쳐",
                    help="촬영된 사진",
                    width="medium"
                )
            },
            hide_index=True,
            use_container_width=True
        )

with tab_logs:
    st.markdown('### 전체 활동 기록')
    col1, col2 = st.columns([1, 4], vertical_alignment='top')
    with col1:
        st.image(image='강아지3.jpg', use_container_width=True)
    with col2:
        with st.expander('검색 필터'):
            st.session_state['search_filter'] = st.multiselect(
                label='검색 필터',
                options=[NONE] + BEHAVIORS,
                default=st.session_state['noti'],
                placeholder='특정 행동을 검색하세요.',
                label_visibility='collapsed'
            )

        filtered_log = st.session_state['log']
        if st.session_state['search_filter']:
            filtered_log = filtered_log[filtered_log['행동'].isin(st.session_state['search_filter'])]

        st.dataframe(
            filtered_log,
            column_config={
                "날짜": st.column_config.TextColumn("날짜"),
                "시간": st.column_config.TextColumn("시간"),
                "행동": st.column_config.TextColumn("행동"),
                "캡쳐": st.column_config.ImageColumn(
                    "캡쳐",
                    help="촬영된 사진",
                    width="medium"
                )
            },
            hide_index=True,
            use_container_width=True
        )

with tab_noti:
    st.markdown('### 알림 설정')
    st.session_state['noti'] = st.multiselect(
        label='반려견이 특정 행동을 했을 때 알림을 받습니다.',
        options=BEHAVIORS,
        default=st.session_state['noti'],
        placeholder='행동을 선택하세요.'
    )

# 📸 캡처 및 테스트 버튼
if st.button(label='📸 캡처 & 테스트', key='1'):
    try:
        image_path = capture_image()  # 웹캠에서 캡처 후 저장
        if image_path:
            behavior = BEHAVIORS[randint(0, len(BEHAVIORS) - 1)] if st.session_state['behavior'] == NONE else NONE
            new_row = get_row(datetime.now(), behavior, image_path)
            st.session_state['log'] = pd.concat([new_row, st.session_state['log']], ignore_index=True)
            st.session_state['behavior'] = behavior
            st.rerun()
    except Exception as e:
        st.error(f"오류 발생: {e}")
