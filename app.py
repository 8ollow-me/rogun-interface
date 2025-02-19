import os
import sys
import pandas as pd
from PIL import Image
import streamlit as st
from datetime import datetime
from random import randint
import base64

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

def get_row(time: datetime, behavior: str):
    """데이터프레임에 새로운 행 추가"""
    return pd.DataFrame({
        '날짜': [time.strftime('%Y-%m-%d')],
        '시간': [time.strftime('%H:%M:%S')],
        '행동': [behavior],
        '캡쳐': [get_image_base64('강아지3.jpg')]
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

# 테스트 버튼
if st.button(label='테스트', key='1'):
    try:
        # 랜덤한 행동 선택
        behavior = BEHAVIORS[randint(0, len(BEHAVIORS) - 1)] if st.session_state['behavior'] == NONE else NONE
        # 새로운 행 추가
        new_row = get_row(datetime.now(), behavior)
        # 로그에 추가
        st.session_state['log'] = pd.concat([new_row, st.session_state['log']], ignore_index=True)
        st.session_state['behavior'] = behavior
        st.rerun()
    except Exception as e:
        st.error(f"Error in test button: {e}")