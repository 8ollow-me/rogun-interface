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

# List of all 13 poses (from your screenshot)
ALL_POSES = [
    "BODYLOWER", "BODYSCRATCH", "BODYSHAKE", "FEETUP", "FOOTUP",
    "HEADING", "LYING", "MOUNTING", "SIT", "TAILING",
    "TAILLOW", "TURN", "WALKRUN"
]

# Initialize session state items if they don't exist yet
if 'log_df' not in st.session_state:
    # DataFrame for detection logs
    st.session_state.log_df = pd.DataFrame(columns=["Timestamp", "Detected Behavior"])

if 'alerts' not in st.session_state:
    # List of triggered alerts
    st.session_state.alerts = []

if 'alert_poses' not in st.session_state:
    # Which poses should trigger alerts?
    # By default, none are selected. You could set a default list if you prefer.
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
    st.write("Live feed from the webcam with detection results below.")
    
    # Placeholder for the video feed area.
    video_placeholder = st.empty()

    # Button to capture a frame from the live stream.
    if st.button("Capture Frame"):
        # --- Backend Integration Point ---
        # Replace the following simulated frame capture with your real webcam feed.
        # Example: frame = your_camera.get_frame()
        #
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        image = Image.fromarray(frame)
        video_placeholder.image(image, caption="Live Feed", use_column_width=True)
        
        # --- Backend Inference Integration ---
        # Replace the following simulated detection with your model's inference result.
        detected_behavior = random.choice(ALL_POSES)
        
        # Log the detection
        log_entry = {
            "Timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "Detected Behavior": detected_behavior
        }
        st.session_state.log_df = st.session_state.log_df.append(log_entry, ignore_index=True)
        
        # Check if the detected pose is in the user-selected alert poses
        if detected_behavior in st.session_state.alert_poses:
            alert_message = {
                "Timestamp": log_entry["Timestamp"],
                "Pose": detected_behavior,
                "Message": f"ALERT: {detected_behavior} detected!"
            }
            st.session_state.alerts.append(alert_message)
        
        st.success(f"Frame Captured! Detected Behavior: {detected_behavior}")

    # Display the five most recent log entries below the video feed
    st.subheader("Recent Detections")
    if len(st.session_state.log_df) > 0:
        st.dataframe(st.session_state.log_df.tail(5).reset_index(drop=True))
    else:
        st.write("No detections yet.")

# ---------------------
# Logs Tab
# ---------------------
with tabs[1]:
    st.header("Logs")
    st.write("All detection logs:")
    if len(st.session_state.log_df) > 0:
        st.dataframe(st.session_state.log_df.reset_index(drop=True))
    else:
        st.write("No logs available.")

# ---------------------
# Alerts Tab
# ---------------------
with tabs[2]:
    st.header("Alerts")
    st.write("Enable or disable alerts for specific poses. Any time a selected pose is detected, it will appear here.")

    # Multi-select widget for choosing which poses to monitor
    st.session_state.alert_poses = st.multiselect(
        "Select Poses to Raise Alerts For",
        ALL_POSES,
        default=st.session_state.alert_poses
    )

    st.subheader("Triggered Alerts")
    if len(st.session_state.alerts) > 0:
        df_alerts = pd.DataFrame(st.session_state.alerts)
        st.dataframe(df_alerts.reset_index(drop=True))
    else:
        st.write("No alerts triggered yet.")

# ---------------------
# Settings Tab
# ---------------------
with tabs[3]:
    st.header("Settings")
    st.write("Configure your detection system here.")

    # Example setting: Selecting a model for inference
    selected_model = st.selectbox("Select Model", ["ResNet", "MobileNet", "Custom Model"])
    st.write(f"Selected Model: {selected_model}")

    # Example collapsible Help/FAQs
    with st.expander("Help / FAQs"):
        st.write("""
        **Q1: How do I start the live stream?**  
        A1: Click the "Capture Frame" button in the Live Stream tab to simulate capturing a frame.  
        
        **Q2: How do I enable alerts for a specific pose?**  
        A2: Go to the Alerts tab, select the pose(s) under "Select Poses to Raise Alerts For." Any time the system detects that pose, an alert will appear in the table below.  
        
        **Q3: Where can I see all my logs?**  
        A3: Check the Logs tab to see a complete history of detected behaviors.  

        **Q4: How do I change the model being used?**  
        A4: Use the "Select Model" dropdown above. In a real deployment, you would load the corresponding model in your backend code.

        **Q5: Where can I get further help?**  
        A5: Contact your system administrator or refer to the official documentation.
        """)

    # Additional settings or configuration options could be added below.
    st.write("More settings can be placed here as needed.")
