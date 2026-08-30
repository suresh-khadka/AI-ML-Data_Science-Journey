import threading
import time

import av
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase

from attention_monitor import AttentionMonitor
from video_player import attention_aware_video_player


class AttentionProcessor(VideoProcessorBase):
    """
    Video processor that runs on every incoming webcam frame in a background
    thread managed by streamlit-webrtc. Uses a lock to safely share the latest
    status with the main Streamlit render loop.
    """

    def __init__(self):
        self.monitor = AttentionMonitor()
        self._lock = threading.Lock()
        self.latest_status = "OK"
        self.latest_ear = 0.0
        self.latest_head_pose = 0.0

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")

        # Run detection - AttentionMonitor.update() should return the status
        # string and also expose last EAR / head pose values for debugging.
        status = self.monitor.update(img)

        with self._lock:
            self.latest_status = status
            self.latest_ear = getattr(self.monitor, "last_ear", 0.0)
            self.latest_head_pose = getattr(self.monitor, "last_head_pose_offset", 0.0)

        # Print to terminal so we can confirm recv() is actually being called
        # and see live values without relying on the Streamlit UI refreshing.
        print(f"[ATTENTION] status={status} ear={self.latest_ear:.3f} head_pose={self.latest_head_pose:.3f}")

        # Return the frame unmodified so the webcam preview still shows.
        return av.VideoFrame.from_ndarray(img, format="bgr24")

    def get_status_snapshot(self):
        """Thread-safe read of the latest computed values."""
        with self._lock:
            return self.latest_status, self.latest_ear, self.latest_head_pose


def render_attention_tab():
    """
    Render the Attention-Aware Playback tab.
    """
    st.header("🎥 Attention-Aware Playback")

    st.markdown(
        """
    This is a local proof-of-concept demonstrating attention-aware video playback.
    The system uses your webcam to detect if you're paying attention to the video:
    - 😴 **SLEEPING**: Eyes closed for sustained period
    - 👀 **DISTRACTED**: Head turned away from screen
    - 🚶 **ABSENT**: No face detected (you left)

    When inattention is detected, the video pauses with an overlay message.
    When you return to normal viewing state, playback resumes automatically.

    *Note: This feature runs locally only and uses a sample video file
    (BigBuckBunny_512kb.mp4). It is not connected to the movie recommendation dataset.*
    """
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Webcam Feed")
        webrtc_ctx = webrtc_streamer(
            key="attention-monitor",
            video_processor_factory=AttentionProcessor,
            rtc_configuration={
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            },
            media_stream_constraints={"video": True, "audio": False},
        )

        status_placeholder = st.empty()
        debug_placeholder = st.empty()

    with col2:
        st.subheader("Video Player")
        video_placeholder = st.empty()

    # --- Live polling loop -------------------------------------------------
    # streamlit-webrtc's recv() runs in a background thread. Nothing forces
    # Streamlit to redraw automatically when that thread's data changes, so
    # we poll the shared processor state on a short interval and re-render
    # the placeholders above. This loop only runs while the stream is active.
    if webrtc_ctx.state.playing:
        while webrtc_ctx.state.playing:
            if webrtc_ctx.video_processor is not None:
                status, ear, head_pose = webrtc_ctx.video_processor.get_status_snapshot()

                with status_placeholder.container():
                    if status == "OK":
                        st.success("Status: Watching normally ✅")
                    elif status == "SLEEPING":
                        st.error("Status: 😴 Sleeping - Eyes closed")
                    elif status == "DISTRACTED":
                        st.warning("Status: 👀 Distracted - Looking away")
                    elif status == "ABSENT":
                        st.info("Status: 🚶 Absent - No face detected")
                    else:
                        st.write(f"Status: {status}")

                with debug_placeholder.container():
                    with st.expander("Debug Values", expanded=True):
                        st.write(f"EAR: {ear:.3f}")
                        st.write(f"Head Pose Offset: {head_pose:.3f}")

                should_pause = status in ("SLEEPING", "DISTRACTED", "ABSENT")
                status_messages = {
                    "SLEEPING": "😴 Paused — you seem to have dozed off",
                    "DISTRACTED": "👀 Paused — you seem distracted",
                    "ABSENT": "🚶 Paused — no one's watching",
                }
                status_message = status_messages.get(status, "")

                with video_placeholder.container():
                    attention_aware_video_player(
                        should_pause=should_pause, status_message=status_message
                    )
            else:
                status_placeholder.info("Initializing detector...")

            time.sleep(0.5)
    else:
        status_placeholder.info("Click 'Start' above and allow camera access to begin.")
        with video_placeholder.container():
            attention_aware_video_player(should_pause=False, status_message="")

    st.markdown("---")
    st.caption(
        "🔒 Local-only proof-of-concept: This feature requires local webcam access "
        "and will not work in cloud deployments."
    )


if __name__ == "__main__":
    render_attention_tab()