import streamlit as st
import time
import random
import numpy as np
from PIL import Image

# List of sample behaviors for simulation
behaviors = [
    "Sitting", "Standing", "Walking", "Running", "Lying Down", "Playing",
    "Eating", "Drinking", "Sleeping", "Barking", "Jumping", "Alert", "Idle"
]

# Set up the page configuration
st.set_page_config(page_title="Dog Behavior Detection", layout="wide")

# App title and description
st.title("Live Dog Behavior Detection")

st.write("This demo simulates a live detection system for dog behaviors using Streamlit.")

# Sidebar configuration for simulation parameters
st.sidebar.header("Configuration")
confidence_threshold = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.5, step=0.1)
simulation_speed = st.sidebar.slider("Simulation Speed (sec/frame)", 0.1, 2.0, 1.0, step=0.1)

# Placeholders for the frame and detection prediction
frame_placeholder = st.empty()
prediction_placeholder = st.empty()

# Button to start the simulation
if st.button("Start Simulation"):
    # Simulation loop (running for 10 frames in this example)
    for i in range(10):
        # Simulate capturing a webcam frame: create a random image
        simulated_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        img = Image.fromarray(simulated_frame)

        # Update the image placeholder with the new frame
        frame_placeholder.image(img, caption=f"Frame {i+1}", use_column_width=True)

        # Simulate a prediction: randomly choose a behavior and confidence score
        predicted_behavior = random.choice(behaviors)
        confidence = round(random.uniform(confidence_threshold, 1.0), 2)

        # Display the prediction
        prediction_placeholder.markdown(
            f"**Detected Behavior:** {predicted_behavior}  \n**Confidence:** {confidence}"
        )

        # Wait before showing the next frame (simulate real-time feed)
        time.sleep(simulation_speed)
