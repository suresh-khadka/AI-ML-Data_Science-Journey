import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
import cv2
import numpy as np
from attention_monitor import AttentionMonitor
from video_player import attention_aware_video_player
import time

class AttentionTransformer(VideoTransformerBase):
    """
    Video transformer that processes frames for attention monitoring.
    """
    def __init__(self):
        self.monitor = AttentionMonitor()
        self.latest_status = "OK"
        self.latest_ear = 0.0
        self.latest_head_pose = 0.0

    def transform(self, frame):
        # Convert frame to numpy array
        img = frame.to_ndarray(format="bgr24")

        # Update attention status
        status = self.monitor.update(img)
        self.latest_status = status

        # For debugging, we could also return the annotated frame
        # For now, just return the original frame
        return img

def render_attention_tab():
    """
    Render the Attention-Aware Playback tab.
    """
    st.header("🎥 Attention-Aware Playback")

    st.markdown("""
    This is a local proof-of-concept demonstrating attention-aware video playback.
    The system uses your webcam to detect if you're paying attention to the video:
    - 😴 **SLEEPING**: Eyes closed for sustained period
    - 👀 **DISTRACTED**: Head turned away from screen
    - 🚶 **ABSENT**: No face detected (you left)

    When inattention is detected, the video pauses with an overlay message.
    When you return to normal viewing state, playback resumes automatically.

    *Note: This feature runs locally only and uses a sample video file (BigBuckBunny_512kb.mp4).
    It is not connected to the movie recommendation dataset.*
    """)

    # Create two columns: left for webcam and status, right for video player
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Webcam Feed")
        # WebRTC streamer for webcam
        webrtc_ctx = webrtc_streamer(
            key="attention-monitor",
            video_transformer_factory=AttentionTransformer,
            rtc_configuration={
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            },
            media_stream_constraints={"video": True, "audio": False},
            async_transform=True,
        )

        # Display status
        if webrtc_ctx.video_processor:
            status = webrtc_ctx.video_transformer.latest_status
            # Status display with emoji and color
            if status == "OK":
                st.success(f"Status: Watching normally ✅")
            elif status == "SLEEPING":
                st.error(f"Status: 😴 Sleeping - Eyes closed")
            elif status == "DISTRACTED":
                st.warning(f"Status: 👀 Distracted - Looking away")
            elif status == "ABSENT":
                st.info(f"Status: 🚶 Absent - No face detected")
            else:
                st.write(f"Status: {status}")

            # Optional: Show debug values
            with st.expander("Debug Values"):
                transformer = webrtc_ctx.video_transformer
                st.write(f"EAR: {transformer.latest_ear:.3f}")
                st.write(f"Head Pose: {transformer.latest_head_pose:.3f}")
        else:
            st.info("Starting webcam... Please wait for the stream to initialize.")

    with col2:
        st.subheader("Video Player")
        # Determine if we should pause based on attention status
        should_pause = False
        status_message = ""

        if webrtc_ctx.video_transformer:
            status = webrtc_ctx.video_transformer.latest_status
            if status == "SLEEPING":
                should_pause = True
                status_message = "😴 Paused — you seem to have dozed off"
            elif status == "DISTRACTED":
                should_pause = True
                status_message = "👀 Paused — you seem distracted"
            elif status == "ABSENT":
                should_pause = True
                status_message = "🚶 Paused — no one's watching"
            else:
                should_pause = False
                status_message = ""

        # Render the video player
        attention_aware_video_player(should_pause=should_pause, status_message=status_message)

    # Add a note about local-only operation
    st.markdown("---")
    st.caption("🔒 Local-only proof-of-concept: This feature requires local webcam access and will not work in cloud deployments.")

if __name__ == "__main__":
    # For testing the tab independently
    render_attention_tab()