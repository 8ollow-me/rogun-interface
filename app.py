import sys
import pandas as pd
from PIL import Image
import streamlit as st
from datetime import datetime
from random import randint
import base64
from io import BytesIO
import os

NONE = '행동 없음'
BEHAVIORS = [
    "BODYLOWER", "BODYSCRATCH", "BODYSHAKE", "FEETUP", "FOOTUP",
    "HEADING", "LYING", "MOUNTING", "SIT", "TAILING",
    "TAILLOW", "TURN", "WALKRUN"
]

# 이미지 디렉토리
IMAGE_DIR = os.path.abspath('images')  # 절대 경로로 변경

def get_last_image():
    image_path = os.path.join(IMAGE_DIR, '강아지3.jpg')
    if not os.path.exists(image_path):
        st.error(f"Image file not found: {image_path}")
    return image_path

# 이미지 파일을 base64로 변환
def image_file_to_base64(filepath: str) -> str:
    try:
        with open(filepath, "rb") as f:
            image = Image.open(f)
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            b64_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return f"data:image/png;base64,{b64_data}"
    except Exception as e:
        st.error(f"Error converting image: {e}")
        return ""

def get_row(time: datetime, behavior: str, image: str): 
    return pd.DataFrame({'날짜': [time.date()], '시간': [time.time()], '행동': [behavior], '캡쳐': [image]})

# Session state initialization
if 'log' not in st.session_state:
    st.session_state['log'] = pd.DataFrame(columns=['날짜', '시간', '행동', '캡쳐'])
if 'behavior_log' not in st.session_state:
    st.session_state['behavior_log'] = pd.DataFrame(columns=['시간', '행동'])  # 🔹 최근 감지된 동작 로그
if 'noti' not in st.session_state:
    st.session_state['noti'] = []
if 'behavior' not in st.session_state:
    st.session_state['behavior'] = NONE
if 'search_filter' not in st.session_state:
    st.session_state['search_filter'] = []
if 'noti_filter' not in st.session_state:
    st.session_state['noti_filter'] = []

# Add a new log entry.
def add_log(time, behavior, image):
    st.session_state['log'] = pd.concat(
        [get_row(time, behavior, image), st.session_state['log']],
        ignore_index=True
    )

    # 🔹 최근 감지된 동작 로그 추가
    new_behavior_log = pd.DataFrame({'시간': [time.strftime("%H:%M:%S")], '행동': [behavior]})
    st.session_state['behavior_log'] = pd.concat(
        [new_behavior_log, st.session_state['behavior_log']],
        ignore_index=True
    )

st.set_page_config(layout="wide")
    
tab_overview, tab_logs, tab_noti = st.tabs(['🔴 실시간 영상', '📋 전체 활동 기록', '🔔 알림 설정'])

with tab_overview:
    col1, col2 = st.columns([25, 10], vertical_alignment='top')
    with col1:
        st.image(image=get_last_image(), use_container_width=True)

    with col2:
        st.markdown('### 최근에 감지된 활동')
        st.dataframe(
            st.session_state['log'],
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
            use_container_width=True,
            height=400
        )

        # 🔹 최근 감지된 동작 리스트 (스크롤 가능)
        st.markdown("#### 최근 감지된 동작")
        st.dataframe(
            st.session_state['behavior_log'],  # 동작 리스트 추가
            hide_index=True,
            use_container_width=True,
            height=200  # 🔹 스크롤 가능하도록 설정
        )

with tab_logs:
    st.markdown('### 전체 활동 기록')
    col1, col2 = st.columns([1, 4], vertical_alignment='top')
    with col1:
        st.image(image=get_last_image(), use_container_width=True)
    with col2:
        with st.expander('검색 필터'):
            st.session_state['search_filter'] = st.multiselect(
                label='검색 필터',
                options=[NONE] + BEHAVIORS,
                default=st.session_state['noti'],
                placeholder='특정 행동을 검색하세요.',
                label_visibility='collapsed'
            )

        log = st.session_state['log']
        if st.session_state['search_filter']:
            log = log[log['행동'].isin(st.session_state['search_filter'])]

        st.dataframe(
            log,
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
            use_container_width=True,
            height=400
        )

with tab_noti:
    st.markdown('### 알림 설정')
    st.session_state['noti_filter'] = st.multiselect(
        label='반려견이 특정 행동을 했을 때 알림을 받습니다.',
        options=BEHAVIORS,
        default=st.session_state['noti'],
        placeholder='행동을 선택하세요.'
    )

if st.button(label='테스트', key='1'):
    # 랜덤 행동 선택: if current behavior is '행동 없음', choose random; else, reset to '행동 없음'
    behavior = BEHAVIORS[randint(0, len(BEHAVIORS) - 1)] if st.session_state['behavior'] == NONE else NONE
    
    # Convert the local image file to a base64 string.
    image_b64 = image_file_to_base64(get_last_image())
    add_log(datetime.now(), behavior, image_b64)
    st.session_state['behavior'] = behavior

    # 알림 설정에 있으면 소리 알림
    if behavior in st.session_state['noti_filter']:
        alert_sound_url = "https://www.soundjay.com/buttons/sounds/button-12.mp3"
        st.markdown(
            f"""
            <audio autoplay>
                <source src="{alert_sound_url}" type="audio/mpeg">
            </audio>
            """,
            unsafe_allow_html=True
        )
    
    st.rerun()
