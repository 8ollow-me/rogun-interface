import gradio as gr
import random
import datetime

log = []


def detect_behavior():
    behaviors = ["The animal is playing.", "The animal is eating.",
                 "The animal is resting.", "The animal is exploring."]
    behavior = random.choice(behaviors)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log.append(f"[{timestamp}] {behavior}")
    return behavior, "\n".join(log)


def video_stream():
    return "path-to-stream.mp4"  # Replace with actual video source


with gr.Blocks(theme="soft") as demo:
    gr.Markdown("# 🐾 Animal Behavior Detection 🐾", elem_id="title")

    with gr.Row():
        video = gr.Video(value=video_stream(),
                         interactive=False, label="Live Stream")

    with gr.Row():
        behavior_text = gr.Textbox(
            label="Detected Behavior", interactive=False)

    with gr.Row():
        log_text = gr.Textbox(label="Behavior Log",
                              interactive=False, lines=10)

    detect_button = gr.Button("🔍 Detect Behavior")
    detect_button.click(detect_behavior, outputs=[behavior_text, log_text])

demo.launch()