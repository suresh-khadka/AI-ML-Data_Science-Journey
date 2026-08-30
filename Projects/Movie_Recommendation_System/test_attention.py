import sys
sys.path.insert(0, '.')

try:
    from attention_monitor import AttentionMonitor
    print("SUCCESS: AttentionMonitor imported")
    monitor = AttentionMonitor()
    print("SUCCESS: AttentionMonitor instantiated")
    print(f"EAR threshold: {monitor.EAR_THRESHOLD}")
    print(f"EAR consecutive frames: {monitor.EAR_CONSECUTIVE_FRAMES}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()