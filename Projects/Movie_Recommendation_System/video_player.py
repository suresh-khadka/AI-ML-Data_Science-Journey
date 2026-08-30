import streamlit as streamlit
import streamlit.components.v1 as components
import os

def attention_aware_video_player(should_pause=False, status_message="", video_path="BigBuckBunny_512kb.mp4"):
    """
    Creates an attention-aware video player component.

    Args:
        should_pause (bool): Whether the video should be paused
        status_message (str): Message to display in overlay when paused
        video_path (str): Path to the video file

    Returns:
        None (renders the component)
    """
    # Get absolute path to video file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    absolute_video_path = os.path.join(base_dir, video_path)

    # Convert to relative path for web serving (Streamlit serves from root)
    # We'll use the filename directly assuming it's in the project root
    video_filename = os.path.basename(video_path)

    # HTML/JavaScript component
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .video-container {{
                position: relative;
                width: 100%;
                max-width: 800px;
                margin: 0 auto;
            }}
            video {{
                width: 100%;
                height: auto;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
            .overlay {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                color: white;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                opacity: 0;
                transition: opacity 0.5s ease;
                border-radius: 10px;
                pointer-events: none;
                font-family: Arial, sans-serif;
            }}
            .overlay.show {{
                opacity: 1;
            }}
            .overlay-icon {{
                font-size: 48px;
                margin-bottom: 20px;
            }}
            .overlay-text {{
                font-size: 24px;
                text-align: center;
                max-width: 80%;
                line-height: 1.4;
            }}
        </style>
    </head>
    <body>
        <div class="video-container">
            <video id="videoPlayer" playsinline>
                <source src="{video_filename}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            <div class="overlay" id="overlay">
                <div class="overlay-icon" id="overlayIcon">⏸️</div>
                <div class="overlay-text" id="overlayText">{status_message}</div>
            </div>
        </div>

        <script>
            // Get video and overlay elements
            const video = document.getElementById("videoPlayer");
            const overlay = document.getElementById("overlay");
            const overlayIcon = document.getElementById("overlayIcon");
            const overlayText = document.getElementById("overlayText");

            // Set up video properties
            video.muted = true;  // Start muted to avoid autoplay issues

            // Function to update player state
            function updatePlayerState(shouldPause, message) {{
                if (shouldPause) {{
                    video.pause();
                    overlay.classList.add('show');
                    overlayText.textContent = message;
                    // Set icon based on message content
                    if (message.includes('dozed off') || message.includes('Sleeping')) {{
                        overlayIcon.textContent = '😴';
                    }} else if (message.includes('distracted') || message.includes('Distracted')) {{
                        overlayIcon.textContent = '👀';
                    }} else if (message.includes('no one') || message.includes('watching')) {{
                        overlayIcon.textContent = '🚶';
                    }} else {{
                        overlayIcon.textContent = '⏸️';
                    }}
                }} else {{
                    video.play();
                    overlay.classList.remove('show');
                }}
            }}

            // Listen for messages from Streamlit
            window.addEventListener('message', function(event) {{
                // Only accept messages from ourselves (for security)
                if (event.data && event.data.type === 'updatePlayer') {{
                    updatePlayerState(event.data.shouldPause, event.data.message);
                }}
            }});

            // Initial state - try to play but most browsers require user interaction
            // We'll start paused and wait for Streamlit to send the first update
            video.pause();

            // Send ready signal to Streamlit
            window.parent.postMessage({{
                type: 'componentReady'
            }}, '*');
        </script>
    </body>
    </html>
    """

    # We need to communicate with the component to update its state
    # We'll use a placeholder approach where we re-render the entire component
    # on each update (Streamlit's normal behavior)

    # For now, let's create a simpler approach without complex JS communication
    # We'll just re-render the HTML with the current state

    # Simpler HTML that we can fully control via Streamlit re-render
    simple_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .video-container {{
                position: relative;
                width: 100%;
                max-width: 800px;
                margin: 0 auto;
            }}
            video {{
                width: 100%;
                height: auto;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
            .overlay {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                color: white;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                opacity: {1.0 if should_pause else 0.0};
                transition: opacity 0.5s ease;
                border-radius: 10px;
                pointer-events: none;
                font-family: Arial, sans-serif;
            }}
            .overlay-icon {{
                font-size: 48px;
                margin-bottom: 20px;
            }}
            .overlay-text {{
                font-size: 24px;
                text-align: center;
                max-width: 80%;
                line-height: 1.4;
            }}
        </style>
    </head>
    <body>
        <div class="video-container">
            <video id="videoPlayer" playsinline {"muted" if should_pause else ""}>
                <source src="{video_filename}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            <div class="overlay">
                <div class="overlay-icon">{"😴" if "dozed off" in status_message.lower() or "sleeping" in status_message.lower()
                                      else "👀" if "distracted" in status_message.lower()
                                      else "🚶" if "no one" in status_message.lower() or "watching" in status_message.lower()
                                      else "⏸️"}</div>
                <div class="overlay-text">{status_message}</div>
            </div>
        </div>
        <script>
            const video = document.getElementById("videoPlayer");
            {"video.pause();" if should_pause else "video.play();"}
        </script>
    </body>
    </html>
    """

    # Render the component
    components.html(simple_html, height=500)