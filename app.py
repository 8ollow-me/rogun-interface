# %%
import streamlit as st
import cv2
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="반려동물 홈캠", layout="wide")

# 제목
st.title("🐾 반려동물 홈캠 서비스")

# 페이지 선택 버튼을 오른쪽 정렬 및 좌우 배치
page_selection_style = """
    <style>
    div[role="radiogroup"] {
        display: flex;
        justify-content: flex-end;
    }
    div[role="radiogroup"] label {
        margin-left: 10px; /* 버튼 간 간격 */
    }
    </style>
"""
st.markdown(page_selection_style, unsafe_allow_html=True)
page = st.radio("", ["Main", "Logs"], horizontal=True, label_visibility="collapsed")

# 세션 상태 초기화
if "webcam_running" not in st.session_state:
    st.session_state["webcam_running"] = False

# 웹캠 및 로그 관련 함수
def get_webcam_height():
    if cap.isOpened():
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return height
    else:
        return 240

def update_log(message):
    global log_messages
    log_messages.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")
    log_messages = log_messages[-5:]
    log_placeholder.markdown(f"""
        <div style="
            background-color: #FFFF00;
            padding: 10px;
            border-radius: 5px;
            overflow-y: scroll;
            height: {webcam_height}px;
            ">
            {'<br>'.join(log_messages)}
        </div>
    """, unsafe_allow_html=True)

# 로그 메시지 리스트
log_messages = []

# 웹캠 열기
cap = cv2.VideoCapture(0)  # 기본 웹캠 사용

if not cap.isOpened():
    st.error("웹캠을 찾을 수 없습니다. 연결을 확인하세요!")
else:
    if page == "Main":
        # 메인 페이지 레이아웃
        col1, col2 = st.columns([3, 1])  # 웹캠:로그창 = 3:1 비율
        webcam_height = get_webcam_height()

        with col1:
            st.subheader("웹캠")
            stframe = st.empty()

        with col2:
            st.subheader("활동")
            log_placeholder = st.empty()

            st.markdown(f"""
                <style>
                    [data-testid="stColumn"]:nth-of-type(2) {{
                        background-color: #FFFF00;
                        height: {webcam_height}px;
                    }}
                </style>
                """, unsafe_allow_html=True)

        while True:
            ret, frame = cap.read()
            if not ret:
                st.error("카메라에서 프레임을 읽을 수 없습니다!")
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            with col1:  # 웹캠 영역에 표시
                stframe.image(frame_rgb, channels="RGB", use_container_width=True)

    elif page == "Logs":
        # 로그 페이지 레이아웃
        col1, col2 = st.columns([1, 3])  # 웹캠:로그창 = 1:3 비율
        webcam_height = get_webcam_height()

        with col1:
            st.subheader("웹캠")
            stframe = st.empty()

        with col2:
            st.subheader("활동")
            log_placeholder = st.empty()

            st.markdown(f"""
                <style>
                    [data-testid="stColumn"]:nth-of-type(2) {{
                        background-color: #FFFF00;
                        height: {webcam_height}px;
                    }}
                    .log-box {{
                        height: 600px;
                    }}
                </style>
                """, unsafe_allow_html=True)

        while True:
            ret, frame = cap.read()
            if not ret:
                st.error("카메라에서 프레임을 읽을 수 없습니다!")
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            with col1:  # 웹캠 영역에 표시
                stframe.image(frame_rgb, channels="RGB", use_container_width=True)

    cap.release()



