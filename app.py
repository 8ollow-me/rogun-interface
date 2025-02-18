import sys
import pandas as pd
from PIL import Image
import streamlit as st
from datetime import datetime


def get_last_image():
    return 'images/rogun.png'


def get_row(time: datetime.date, behavior: str, image: str): 
    return pd.DataFrame({'날짜': [time.date()], '시간': [time.time()], '행동': [behavior], '캡쳐': [image]})


# 세션 데이터
if 'log' not in st.session_state:
    st.session_state['log'] = pd.DataFrame(columns=['날짜', '시간', '행동', '캡쳐'])

# 이벤트
def add_log(time, behavior, image):
    st.session_state['log'] = pd.concat(
        [get_row(time, behavior, image), st.session_state['log']],
        ignore_index=True
    )

# 뷰
st.set_page_config(layout="wide")

if st.button(label='테스트', key='1'):
    add_log(datetime.now(), '뭐지?', 'G:\\zer0ken\\rogun-interface\\images\\rogun.png')
    st.rerun()
    
tab_overview, tab_logs, tab_config = st.tabs(['🔴 실시간 영상', '📋 활동 기록',  '⚙️ 설정'])

with tab_overview:
    col1, col2 = st.columns([1, 3], vertical_alignment='top')
    with col1:
        st.markdown('### 🔔 최근에 감지된 활동')
        st.dataframe(
            st.session_state['log'][:10],
            column_config={
                "캡쳐": st.column_config.ImageColumn("캡쳐")
            },
            use_container_width=True, 
            hide_index=True
        )
    with col2:
        st.image(image=get_last_image(), use_container_width=True)

with tab_logs:
    st.markdown('### 📋 전체 활동 기록')
    col1, col2 = st.columns([1, 4], vertical_alignment='top')
    with col1:
        st.image(image=get_last_image(), use_container_width=True)
    with col2:
        log = st.session_state['log']
        groups = log.groupby('날짜')
        for group in groups[::-1]:
            date, df = group
            with st.expander(date.strftime(r'%Y년 %m월 %d일')):
                st.dataframe(df.drop(columns=['날짜']), use_container_width=True, hide_index=True)

with tab_config:
    st.markdown('뭔가 뭔가임')
