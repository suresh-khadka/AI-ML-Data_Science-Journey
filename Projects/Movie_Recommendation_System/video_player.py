import base64
import os

import streamlit as st
import streamlit.components.v1 as components

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VIDEO_PATH = os.path.join(BASE_DIR, "BigBuckBunny_512kb.mp4")


@st.cache_data
def _load_video_base64(video_path: str) -> str:
    """
    Read a local video file once and cache it as a base64 string so it can be
    embedded directly into the HTML component via a data: URL. This avoids
    relying on Streamlit serving arbitrary local files, which components.html()
    (an isolated iframe) cannot resolve by bare filename or relative path.
    """
    with open(video_path, "rb") as f:
        video_bytes = f.read()
    return base64.b64encode(video_bytes).decode("utf-8")


def attention_aware_video_player(
    should_pause: bool,
    status_message: str = "",
    video_path: str = DEFAULT_VIDEO_PATH,
    height: int = 380,
):
    """
    Renders a full-featured video player (play/pause, seek bar, volume,
    fullscreen - same controls as any standard HTML5 <video controls> player)
    with an added attention-aware auto-pause overlay driven from Python.

    should_pause: True to force-pause the video and show the overlay right now.
    status_message: text shown inside the overlay when auto-paused.
    video_path: absolute path to the video file.
    height: pixel height of the rendered component.
    """
    if not os.path.exists(video_path):
        st.error(f"Sample video not found at: {video_path}")
        return

    video_b64 = _load_video_base64(video_path)

    lowered = status_message.lower()
    if "dozed off" in lowered or "sleep" in lowered:
        icon = "😴"
    elif "distract" in lowered:
        icon = "👀"
    elif "no one" in lowered or "absent" in lowered:
        icon = "🚶"
    else:
        icon = "⏸️"

    safe_message = status_message.replace('"', "&quot;").replace("'", "&#39;")
    pause_js = "true" if should_pause else "false"

    html_code = f"""
    <div style="position: relative; width: 100%; max-width: 560px; margin: 0 auto;">
        <video id="attention-video" width="100%" controls playsinline
               style="border-radius: 10px; display: block; box-shadow: 0 4px 10px rgba(0,0,0,0.25);">
            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        <div id="pause-overlay" style="
                position: absolute; top: 0; left: 0; right: 0;
                height: calc(100% - 40px);
                background: rgba(0,0,0,0.75); color: white;
                display: {"flex" if should_pause else "none"};
                flex-direction: column; align-items: center; justify-content: center;
                text-align: center; border-radius: 10px 10px 0 0; padding: 1rem;
                box-sizing: border-box; pointer-events: none;
                font-family: -apple-system, Segoe UI, Roboto, sans-serif;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
            <div style="font-size: 1.05rem; font-weight: 600;">{safe_message}</div>
        </div>
    </div>

    <script>
        (function() {{
            const video = document.getElementById('attention-video');
            const overlay = document.getElementById('pause-overlay');
            const shouldPause = {pause_js};
            if (!video) return;

            if (shouldPause) {{
                // Auto-pause due to inattention. Remember that this pause was
                // triggered by the system, not the user, so we know it's safe
                // to auto-resume later.
                if (!video.paused) {{
                    video.dataset.autoPaused = "true";
                    video.pause();
                }}
                overlay.style.display = 'flex';
            }} else {{
                overlay.style.display = 'none';
                // Only auto-resume if WE paused it automatically. If the user
                // manually paused the video themselves (dataset.autoPaused is
                // not set), respect that and do not force it to play again.
                if (video.paused && video.dataset.autoPaused === "true") {{
                    video.play().catch(function(err) {{
                        console.log('play() failed:', err);
                    }});
                }}
                video.dataset.autoPaused = "false";
            }}

            // If the user manually pauses/plays via the native controls,
            // clear the auto-pause flag so we don't fight their choice.
            video.onpause = function() {{
                if (!shouldPause) {{
                    video.dataset.autoPaused = "false";
                }}
            }};
        }})();
    </script>
    """

    components.html(html_code, height=height)