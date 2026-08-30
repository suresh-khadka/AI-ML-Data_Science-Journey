# Simple test to verify basic imports work
print("Testing basic imports...")

try:
    import cv2
    print("✓ OpenCV imported")
except Exception as e:
    print(f"✗ OpenCV import failed: {e}")

try:
    import mediapipe as mp
    print(f"✓ MediaPipe imported (version: {mp.__version__})")
except Exception as e:
    print(f"✗ MediaPipe import failed: {e}")

try:
    import numpy as np
    print("✓ NumPy imported")
except Exception as e:
    print(f"✗ NumPy import failed: {e}")

try:
    import streamlit as st
    print("✓ Streamlit imported")
except Exception as e:
    print(f"✗ Streamlit import failed: {e}")

try:
    from streamlit_webrtc import webrtc_streamer
    print("✓ Streamlit-WebRTC imported")
except Exception as e:
    print(f"✗ Streamlit-WebRTC import failed: {e}")

try:
    import av
    print("✓ AV imported")
except Exception as e:
    print(f"✗ AV import failed: {e}")

print("\nTesting our custom modules...")

try:
    from attention_monitor import AttentionMonitor
    print("✓ AttentionMonitor imported")
except Exception as e:
    print(f"✗ AttentionMonitor import failed: {e}")

try:
    from video_player import attention_aware_video_player
    print("✓ Video player imported")
except Exception as e:
    print(f"✗ Video player import failed: {e}")

try:
    from attention_tab import render_attention_tab
    print("✓ Attention tab imported")
except Exception as e:
    print(f"✗ Attention tab import failed: {e}")

print("\nBasic import test completed.")