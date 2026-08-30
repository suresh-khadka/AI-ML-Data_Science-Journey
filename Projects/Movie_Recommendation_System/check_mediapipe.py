import mediapipe
print("MediaPipe version:", mediapipe.__version__)
print("Dir:", [x for x in dir(mediapipe) if not x.startswith('_')])