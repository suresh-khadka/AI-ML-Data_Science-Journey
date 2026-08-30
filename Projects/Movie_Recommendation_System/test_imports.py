import sys
print("Python version:", sys.version)
print("Testing imports...")
try:
    import cv2
    print("✓ OpenCV imported successfully")
except Exception as e:
    print("✗ OpenCV import failed:", e)

try:
    import mediapipe
    print("✓ MediaPipe imported successfully")
    print("  Version:", mediapipe.__version__)
except Exception as e:
    print("✗ MediaPipe import failed:", e)

try:
    import numpy as np
    print("✓ NumPy imported successfully")
except Exception as e:
    print("✗ NumPy import failed:", e)

try:
    import streamlit as st
    print("✓ Streamlit imported successfully")
except Exception as e:
    print("✗ Streamlit import failed:", e)

try:
    from streamlit_webrtc import webrtc_streamer
    print("✓ Streamlit-WebRTC imported successfully")
except Exception as e:
    print("✗ Streamlit-WebRTC import failed:", e)

try:
    import av
    print("✓ AV imported successfully")
except Exception as e:
    print("✗ AV import failed:", e)

print("\nTesting custom modules...")
try:
    from attention_monitor import AttentionMonitor
    print("✓ AttentionMonitor imported successfully")
except Exception as e:
    print("✗ AttentionMonitor import failed:", e)
    import traceback
    traceback.print_exc()

try:
    from video_player import attention_aware_video_player
    print("✓ Video player imported successfully")
except Exception as e:
    print("✗ Video player import failed:", e)

try:
    from attention_tab import render_attention_tab
    print("✓ Attention tab imported successfully")
except Exception as e:
    print("✗ Attention tab import failed:", e)