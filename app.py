import sys
import pandas as pd
from PIL import Image
import streamlit as st
from datetime import datetime
from random import randint

NONE = '행동 없음'
BEHAVIORS = [
    "BODYLOWER", "BODYSCRATCH", "BODYSHAKE", "FEETUP", "FOOTUP",
    "HEADING", "LYING", "MOUNTING", "SIT", "TAILING",
    "TAILLOW", "TURN", "WALKRUN"
]


def get_last_image():
    return 'images/rogun.png'

def get_row(time: datetime.date, behavior: str, image: str): 
    return pd.DataFrame({'날짜': [time.date()], '시간': [time.time()], '행동': [behavior], '캡쳐': [image]})


# 세션 데이터
if 'log' not in st.session_state:
    st.session_state['log'] = pd.DataFrame(columns=['날짜', '시간', '행동', '캡쳐'])
if 'noti' not in st.session_state:
    st.session_state['noti'] = []
if 'behavior' not in st.session_state:
    st.session_state['behavior'] = NONE
if 'search_filter' not in st.session_state:
    st.session_state['search_filter'] = []
if 'noti_filter' not in st.session_state:
    st.session_state['noti_filter'] = []

# 이벤트
def add_log(time, behavior, image):
    st.session_state['log'] = pd.concat(
        [get_row(time, behavior, image), st.session_state['log']],
        ignore_index=True
    )

# 뷰
st.set_page_config(layout="wide")
    
tab_overview, tab_logs, tab_noti = st.tabs(['🔴 실시간 영상', '📋 전체 활동 기록',  '🔔 알림 설정'])

with tab_overview:
    col1, col2 = st.columns([25, 10], vertical_alignment='top')
    with col1:
        st.image(image=get_last_image(), use_container_width=True)
    with col2:
        st.markdown('### 최근에 감지된 활동')
        st.dataframe(
            st.session_state['log'][:10],
            column_config={
                "캡쳐": st.column_config.ImageColumn("캡쳐")
            },
            use_container_width=True, 
            hide_index=True
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
                options= [NONE] + BEHAVIORS,
                default=st.session_state['noti'],
                placeholder='특정 행동을 검색하세요.',
                label_visibility='collapsed'
            )

        log = st.session_state['log']
        groups = log.groupby('날짜')
        is_first_group = True
        has_no_data = True
        
        for group in list(groups)[::-1]:
            date, df = group
            if st.session_state['search_filter']:
                df = df[df['행동'].isin(st.session_state['search_filter'])]
                if df.empty:
                    continue
            has_no_data = False
            date = date.strftime(r'%Y년 %m월 %d일')
            with st.expander(f'{date} ({len(df)})', expanded=is_first_group):
                st.dataframe(df.drop(columns=['날짜']), use_container_width=True, hide_index=True)
            is_first_group = False
            
        if has_no_data:
            st.caption('행동 기록이 없습니다.')
    
with tab_noti:
    st.markdown('### 알림 설정')
    st.session_state['noti_filter'] = st.multiselect(
        label='반려견이 특정 행동을 했을 때 알림을 받습니다.',
        options=BEHAVIORS,
        default=st.session_state['noti'],
        placeholder='행동을 선택하세요.'
    )

if st.button(label='테스트', key='1'):
    # 랜덤 행동 선택
    behavior = BEHAVIORS[randint(0, len(BEHAVIORS) - 1)] if st.session_state['behavior'] == NONE else NONE
    
    # 로그 추가
    add_log(datetime.now(), behavior, '/Desktop/AI/rogun-interface/images/rogun.png')
    st.session_state['behavior'] = behavior

    # 알림 설정에 있으면 소리 알림
    if behavior in st.session_state['noti_filter']:
        alert_sound_url = "https://www.soundjay.com/buttons/sounds/button-12.mp3"  # 원하는 사운드로 여기만 바꾸면 됩니다
        st.markdown(
            f"""
            <audio autoplay>
                <source src="{alert_sound_url}" type="audio/mpeg">
            </audio>
            """,
            unsafe_allow_html=True
        )
    
    st.rerun()
