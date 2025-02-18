import streamlit as st
import time
import random
import numpy as np
import pandas as pd
from PIL import Image

# ---------------------
# Page and Session Setup
# ---------------------
st.set_page_config(page_title="Dog Behavior Detection", layout="wide")

# List of all 13 poses
ALL_POSES = [
    "BODYLOWER", "BODYSCRATCH", "BODYSHAKE", "FEETUP", "FOOTUP",
    "HEADING", "LYING", "MOUNTING", "SIT", "TAILING",
    "TAILLOW", "TURN", "WALKRUN"
]

# Initialize session state items if they don't exist yet
if 'log_df' not in st.session_state:
    st.session_state.log_df = pd.DataFrame(columns=["Timestamp", "Detected Behavior"])

if 'alerts' not in st.session_state:
    st.session_state.alerts = []

if 'alert_poses' not in st.session_state:
    st.session_state.alert_poses = []

# ---------------------
# Create Tabbed Layout
# ---------------------
tabs = st.tabs(["Live Stream", "Logs", "Alerts", "Settings"])

# ---------------------
# Live Stream Tab
# ---------------------
with tabs[0]:
    st.header("Live Stream")
    st.write("라이브 웹캠 피드를 시뮬레이션합니다. 실제 제품에서는 실제 카메라 스트림이 표시됩니다.")

    # Placeholder for the video feed area
    video_placeholder = st.empty()

    # --- Backend Integration Point ---
    # Replace this with your actual webcam feed or video stream.
    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    image = Image.fromarray(frame)
    video_placeholder.image(image, caption="Simulated Live Feed", use_column_width=True)

    # --- ResNet Inference Integration ---
    # Replace the random detection below with your ResNet model inference.
    detected_behavior = random.choice(ALL_POSES)

    # Display a sample string showing how the detection will be displayed
    st.info(f"Detected Behavior: {detected_behavior}")

    # Log the detection using pd.concat instead of append
    log_entry = pd.DataFrame([{
        "Timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "Detected Behavior": detected_behavior
    }])
    st.session_state.log_df = pd.concat([st.session_state.log_df, log_entry], ignore_index=True)

    # Check if the detected pose is in the user-selected alert poses
    if detected_behavior in st.session_state.alert_poses:
        alert_message = {
            "Timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "Pose": detected_behavior,
            "Message": f"ALERT: {detected_behavior} detected!"
        }
        st.session_state.alerts.append(alert_message)

    # Display the five most recent log entries
    st.subheader("Recent Detections")
    if not st.session_state.log_df.empty:
        st.dataframe(st.session_state.log_df.tail(5).reset_index(drop=True))
    else:
        st.write("No detections yet.")

# ---------------------
# Logs Tab
# ---------------------
with tabs[1]:
    st.header("Logs")
    st.write("모든 감지 기록:")
    if not st.session_state.log_df.empty:
        st.dataframe(st.session_state.log_df.reset_index(drop=True))
    else:
        st.write("로그가 없습니다.")

# ---------------------
# Alerts Tab
# ---------------------
with tabs[2]:
    st.header("Alerts")
    st.write("특정 포즈 감지 시 경고를 표시합니다.")

    # Multi-select widget for choosing which poses to monitor
    st.session_state.alert_poses = st.multiselect(
        "알림을 받을 포즈 선택",
        ALL_POSES,
        default=st.session_state.alert_poses
    )

    st.subheader("Triggered Alerts")
    if st.session_state.alerts:
        df_alerts = pd.DataFrame(st.session_state.alerts)
        st.dataframe(df_alerts.reset_index(drop=True))
    else:
        st.write("아직 경고가 없습니다.")

# ---------------------
# Settings Tab
# ---------------------
with tabs[3]:
    st.header("Settings")
    st.write("검출 시스템 환경 설정")

    # Help/FAQ in Korean
    with st.expander("도움말 / 자주 묻는 질문 (FAQs)"):
        st.write("""
        **Q1: 라이브 스트림은 어떻게 시작하나요?**  
        A1: "Live Stream" 탭에서 실제 카메라 스트림을 연결하면, 자동으로 영상이 표시되고 감지 결과가 업데이트됩니다.  
        
        **Q2: 특정 포즈에 대한 알림을 어떻게 설정하나요?**  
        A2: "Alerts" 탭에서 "알림을 받을 포즈 선택" 항목에서 원하는 포즈를 선택하세요. 시스템이 해당 포즈를 감지하면, "Triggered Alerts" 테이블에 경고가 표시됩니다.  
        
        **Q3: 전체 로그는 어디에서 볼 수 있나요?**  
        A3: "Logs" 탭에서 모든 감지 기록을 확인할 수 있습니다.  
        
        **Q4: 기타 도움이 필요하면 어디서 찾을 수 있나요?**  
        A4: 시스템 관리자에게 문의하거나 추가 문서를 참조하세요.
        """)

    st.write("추가 설정을 이곳에 추가할 수 있습니다.")
