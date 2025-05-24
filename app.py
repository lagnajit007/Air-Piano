import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, ClientSettings
import av
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np
import time

# Hand detector initialization
detector = HandDetector(detectionCon=0.8)

# Chord Map (simplified for demo)
chords = {
    "left": {
        "thumb": "C Major",
        "index": "D Minor",
        "middle": "E Minor",
        "ring": "F Major",
        "pinky": "G Major"
    },
    "right": {
        "thumb": "A Minor",
        "index": "B Diminished",
        "middle": "C7",
        "ring": "D7",
        "pinky": "E7"
    }
}

class VideoProcessor(VideoProcessorBase):
    def __init__(self):
        self.prev_states = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, draw=True)

        if hands:
            for hand in hands:
                hand_type = "right" if hand["type"] == "Left" else "left"
                fingers = detector.fingersUp(hand)
                finger_names = ["thumb", "index", "middle", "ring", "pinky"]

                for i, finger in enumerate(finger_names):
                    if finger in chords[hand_type]:
                        if fingers[i] == 1 and self.prev_states[hand_type][finger] == 0:
                            chord_name = chords[hand_type][finger]
                            cv2.putText(img, f"🎵 {chord_name}", (50, 100 + 30*i),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        self.prev_states[hand_type][finger] = fingers[i]

        return av.VideoFrame.from_ndarray(img, format="bgr24")


st.title("🎹 Hand-Controlled MIDI Chord Player (Web Demo)")
st.markdown("Raise your fingers to simulate playing chords!")

webrtc_streamer(
    key="midi-chords",
    video_processor_factory=VideoProcessor,
    client_settings=ClientSettings(
        media_stream_constraints={"video": True, "audio": False},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    )
)
