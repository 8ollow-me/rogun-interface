import pandas as pd
from datetime import datetime
from random import randint
import streamlit as st

NONE = '행동 없음'
BEHAVIORS = [
    "BODYLOWER", "BODYSCRATCH", "BODYSHAKE", "FEETUP", "FOOTUP",
    "HEADING", "LYING", "MOUNTING", "SIT", "TAILING",
    "TAILLOW", "TURN", "WALKRUN"
]
BEEPS = {
    '알림음 끄기': '',
    '기본 알림음': 'https://www.soundjay.com/buttons/sounds/beep-07a.mp3'
}


def get_last_image():
    return 'images/rogun.png'


def get_row(time: datetime.date, behavior: str, image: str): 
    return pd.DataFrame({'날짜': [time.date()], '시간': [time.time()], '행동': [behavior], '캡쳐': [image]})


# =========
# 세션 상태
# =========
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
if 'beep' not in st.session_state:
    st.session_state['beep'] = list(BEEPS.keys())[0]


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
    test = col2

with tab_logs:
    st.markdown('### 전체 활동 기록')
    col1, col2 = st.columns([1, 4], vertical_alignment='top')
    with col1:
        st.image(image=get_last_image(), use_container_width=True)
        behavior_bar_small = st.empty()
    with col2:
        with st.expander('검색 필터'):
            st.session_state['search_filter'] = st.multiselect(
                label='검색 필터',
                options= [NONE] + BEHAVIORS,
                default=st.session_state['noti'],
                placeholder='특정 행동을 검색하세요.',
                label_visibility='collapsed'
            )
        log_dataframe_list = st.empty()

    
with tab_noti:
    st.markdown('### 알림 설정')
    st.session_state['noti_filter'] = st.multiselect(
        label='반려견이 특정 행동을 했을 때 알림을 받습니다.',
        options=BEHAVIORS,
        default=st.session_state['noti'],
        placeholder='행동을 선택하세요.'
    )
    with st.expander('알림음 설정'):
        st.session_state['beep'] = st.radio(
            label='알림음 설정', 
            options=list(BEEPS.keys()),
            index=1,
            label_visibility='collapsed'
        )


# ==================
# 컴포넌트 갱신 함수
# ==================
def update_log_dataframe_brief():
    log = st.session_state['log']
    log_dataframe_brief.dataframe(
        log[:10],
        column_config={
            "캡쳐": st.column_config.ImageColumn("캡쳐")
        },
        use_container_width=True, 
        hide_index=True
    )


def update_log_dataframe_list():
    log = st.session_state['log']
    groups = log.groupby('날짜')
    is_first_group = True
    has_no_data = True
    
    with log_dataframe_list:
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


def update_behavior_bar_large():
    log = st.session_state['log']
    if log.empty or log.loc[0, '행동'] == NONE:
        behavior_bar_large.info(f'행동이 감지되지 않았습니다.')
    elif log.loc[0,'행동'] in st.session_state['noti_filter']:
        behavior_bar_large.warning(f'🔔 행동이 감지됐습니다: **{log.loc[0,'행동']}**')
    elif log.loc[0,'행동'] != NONE:
        behavior_bar_large.info(f'행동이 감지됐습니다: **{log.loc[0,'행동']}**')


def update_behavior_bar_small():
    log = st.session_state['log']
    if log.empty or log.loc[0, '행동'] == NONE:
        behavior_bar_small.info(f'🐶 {NONE if log.empty else log.loc[0,'행동']}')
    elif log.loc[0, '행동'] in st.session_state['noti_filter']:
        behavior_bar_small.warning(f'🐕 **{log.loc[0,'행동']}**')
    else:
        behavior_bar_small.info(f'🐕 {NONE if log.empty else log.loc[0,'행동']}')


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
    st.session_state['log'] = pd.concat(
        [get_row(time, behavior, image), st.session_state['log']],
        ignore_index=True
    )
    st.session_state['behavior'] = behavior
    if behavior in st.session_state['noti_filter']:
        st.markdown(
            f'<audio autoplay><source src="{BEEPS[st.session_state['beep']]}" type="audio/mpeg"></audio>',
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
import time
while True:
    behavior = BEHAVIORS[randint(0, len(BEHAVIORS) - 1)] if st.session_state.behavior == NONE else NONE
    add_log(datetime.now(), behavior, 'G:\\zer0ken\\rogun-interface\\images\\rogun.png')
    time.sleep(5)