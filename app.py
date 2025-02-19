import os
import base64
import pandas as pd
import streamlit as st
from io import BytesIO
from PIL import Image
from random import randint
from datetime import datetime

NONE = '행동 없음'
BEHAVIORS = [
    "BODYLOWER", "BODYSCRATCH", "BODYSHAKE", "FEETUP", "FOOTUP",
    "HEADING", "LYING", "MOUNTING", "SIT", "TAILING",
    "TAILLOW", "TURN", "WALKRUN"
]
BEEPS = {
    '알림음 끄기': '',
    '기본 알림음': 'https://www.soundjay.com/buttons/sounds/beep-07a.mp3',
    '멍멍': 'https://t1.daumcdn.net/cfile/tistory/99CC98395CE6F54B0A'
}


def get_last_image():
    return image_to_base64('images/rogun.png')


def get_row(time: datetime.date, behavior: str, image: str): 
    return pd.DataFrame({'날짜': [time.date()], '시간': [time.time()], '행동': [behavior], '캡쳐': [image]})


def image_to_base64(filepath: str) -> str:
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


def load_logs():
    dataframes = []
    for filename in os.listdir('logs/'):
        if filename.endswith('.csv'):
            dataframes.append(pd.read_csv(f'logs/{filename}'))
    if not dataframes:
        return pd.DataFrame(columns=['날짜', '시간', '행동', '캡쳐'])
    df = pd.concat(dataframes[::-1])
    df['datetime'] = df['날짜'].add([' '] * len(df)).add(df['시간'])
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['날짜'] = df['datetime'].apply(datetime.date)
    df['시간'] = df['datetime'].apply(datetime.time)
    return df.drop(columns=['datetime'])


# =========
# 세션 상태
# =========
if 'log' not in st.session_state:
    st.session_state.log = load_logs()
if 'behavior' not in st.session_state:
    st.session_state.behavior = NONE
if 'search_filter' not in st.session_state:
    st.session_state.search_filter = []
if 'noti_filter' not in st.session_state:
    st.session_state.noti_filter = []
if 'beep' not in st.session_state:
    st.session_state.beep = list(BEEPS.keys())[0]


# =======
# 뷰 생성
# =======
st.set_page_config(layout="wide")

tab_overview, tab_logs, tab_noti = st.tabs(['🔴 실시간 영상', '📋 전체 활동 기록',  '🔔 알림 설정'])

with tab_overview:
    col1, col2 = st.columns([25, 10], vertical_alignment='top')
    with col1:
        st.image(image=get_last_image(), use_container_width=True)
    with col2:
        st.markdown('### 최근에 감지된 활동')
        log_dataframe_brief = st.empty()
        behavior_bar_large = st.empty()

with tab_logs:
    st.markdown('### 전체 활동 기록')
    col1, col2 = st.columns([1, 4], vertical_alignment='top')
    with col1:
        st.image(image=get_last_image(), use_container_width=True)
        behavior_bar_small = st.empty()
    with col2:
        with st.expander('검색 필터'):
            st.session_state.search_filter = st.multiselect(
                label='검색 필터',
                options= [NONE] + BEHAVIORS,
                placeholder='특정 행동을 검색하세요.',
                label_visibility='collapsed'
            )
        log_dataframe_list = st.container()

    
with tab_noti:
    st.markdown('### 알림 설정')
    st.session_state.noti_filter = st.multiselect(
        label='반려견이 특정 행동을 했을 때 알림을 받습니다.',
        options=BEHAVIORS,
        placeholder='알림을 받을 행동을 선택하세요.'
    )
    with st.expander('알림음 설정'):
        st.session_state.beep = st.radio(
            label='알림음 설정', 
            options=list(BEEPS.keys()),
            index=1,
            label_visibility='collapsed'
        )


# ==================
# 컴포넌트 갱신 함수
# ==================
def update_log_dataframe_brief():
    log = st.session_state.log
    log_dataframe_brief.dataframe(
        log[:10],
        column_config={
            "캡쳐": st.column_config.ImageColumn("캡쳐")
        },
        use_container_width=True, 
        hide_index=True
    )


def update_log_dataframe_list():
    log = st.session_state.log
    groups = log.groupby('날짜')
    is_first_group = True
    has_no_data = True
    
    with log_dataframe_list.container():
        for group in list(groups)[::-1]:
            date, df = group
            if st.session_state.search_filter:
                df = df[df['행동'].isin(st.session_state.search_filter)]
                if df.empty:
                    continue
            has_no_data = False
            date = date.strftime(r'%Y년 %m월 %d일')
            with st.expander(f'{date} ({len(df)})', expanded=is_first_group):
                st.dataframe(
                    df.drop(columns=['날짜']), 
                    column_config={
                        "캡쳐": st.column_config.ImageColumn("캡쳐")
                    },
                    use_container_width=True, 
                    hide_index=True
                )
            is_first_group = False
        if has_no_data:
            st.caption('행동 기록이 없습니다.')


def update_behavior_bar_large():
    behavior = st.session_state.behavior
    if behavior == NONE:
        behavior_bar_large.info(f'행동이 감지되지 않았습니다.')
    elif behavior in st.session_state.noti_filter:
        behavior_bar_large.warning(f'🔔 행동이 감지됐습니다: **{behavior}**')
    else:
        behavior_bar_large.info(f'행동이 감지됐습니다: **{behavior}**')


def update_behavior_bar_small():
    behavior = st.session_state.behavior
    if behavior == NONE:
        behavior_bar_small.info(f'🐶 {behavior}')
    elif behavior in st.session_state.noti_filter:
        behavior_bar_small.warning(f'🐕 **{behavior}**')
    else:
        behavior_bar_small.info(f'🐕 {behavior}')


# ===============
# 컴포넌트 초기화
# ===============
update_log_dataframe_brief()
update_log_dataframe_list()
update_behavior_bar_large()
update_behavior_bar_small()


# ======
# 이벤트
# ======
def add_log(time, behavior, image):
    st.session_state.log = pd.concat(
        [get_row(time, behavior, image_to_base64(image)), st.session_state.log],
        ignore_index=True
    )
    st.session_state.behavior = behavior
    if behavior in st.session_state.noti_filter:
        st.markdown(
            f'<audio autoplay><source src="{BEEPS[st.session_state.beep]}" type="audio/mpeg"></audio>',
            unsafe_allow_html=True
        )
    on_add_log()
    
def on_add_log():
    update_log_dataframe_brief()
    update_log_dataframe_list()
    update_behavior_bar_large()
    update_behavior_bar_small()


# ===========
# 테스트 코드
# ===========
# import time
# while True:
#     behavior = BEHAVIORS[randint(0, len(BEHAVIORS) - 1)] if st.session_state.behavior == NONE else NONE
#     add_log(datetime.now(), behavior, 'C:\\Projects\\rogun_interface\\images\\rogun.png')
#     time.sleep(5)