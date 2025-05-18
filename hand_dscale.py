import cv2
import threading
import pygame.midi
import time
import math
from cvzone.HandTrackingModule import HandDetector

# Initialize Pygame MIDI
pygame.midi.init()
player = pygame.midi.Output(0)

# Instrument Map
instruments = {
    0: "Acoustic Grand Piano",
    27: "Electric Guitar (jazz)",
    29: "Electric Guitar (muted)",
    40: "Violin",
    48: "String Ensemble",
    60: "French Horn",
    75: "Indian Flute",
    80: "Square Lead"
}
instrument_keys = list(instruments.keys())
current_instrument_index = 0
player.set_instrument(instrument_keys[current_instrument_index])

# Initialize Hand Detector
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8)

# Chord Mapping
chords = {
    "left": {
        "thumb": [50, 54, 57],
        "index": [52, 55, 59],
        "middle": [54, 57, 61],
        "ring": [55, 59, 62],
        "pinky": [57, 61, 64]
    },
    "right": {
        "thumb": [62, 66, 69],
        "index": [64, 67, 71],
        "middle": [66, 69, 73],
        "ring": [67, 71, 74],
        "pinky": [69, 73, 76]
    }
}

SUSTAIN_TIME = 2.0
prev_states = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}
latest_action = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}

# Calibration
print("\n✋ Show open hand for calibration...")
time.sleep(2)
calibration_data = []
calibrated_height = 300  # Default fallback
for _ in range(30):
    success, img = cap.read()
    if not success:
        continue
    img = cv2.flip(img, 1)
    hands, _ = detector.findHands(img, draw=False)
    if hands:
        hand = hands[0]
        lmList = hand['lmList']
        if len(lmList) >= 13:
            avg_y = sum([pt[1] for pt in lmList[8:13]]) / 5
            calibration_data.append(avg_y)

if calibration_data:
    calibrated_height = sum(calibration_data) / len(calibration_data)
print(f"\u2705 Calibrated height: {calibrated_height:.2f}\n")

# Draw animated wave
wave_phase = 0

def draw_wave(img, base_y, phase):
    for x in range(0, img.shape[1], 15):
        y = int(base_y + 15 * math.sin((x + phase) * 0.07))
        cv2.circle(img, (x, y), 2, (255, 255, 255), -1)
        
        


def stop_chord_after_delay(chord_notes, hand_type, finger, action_time):
    # Optional: simulate vibrato effect by quickly turning the note off and on
    if instruments[instrument_keys[current_instrument_index]].startswith("Indian Flute"):
        for _ in range(2):
            for note in chord_notes:
                player.note_off(note, 127)
            time.sleep(0.05)
            for note in chord_notes:
                player.note_on(note, 80)
            time.sleep(0.05)
    time.sleep(SUSTAIN_TIME)
    if latest_action[hand_type][finger] == action_time:
        for note in chord_notes:
            player.note_off(note, 127)

cv2.namedWindow("Hand Tracking MIDI Chords", cv2.WINDOW_NORMAL)

while True:
    success, img = cap.read()
    if not success:
        print("❌ Camera not capturing frames")
        continue

    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, draw=True, flipType=False)

    cv2.putText(img, "Raise fingers to play chords | Press 'i' to switch instrument | 'q' to quit",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
    cv2.putText(img, f"Instrument: {instruments[instrument_keys[current_instrument_index]]}",
                (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 255), 2)

    if hands:
        for hand in hands:
            hand_type = "right" if hand["type"] == "Left" else "left"
            fingers = detector.fingersUp(hand)
            finger_names = ["thumb", "index", "middle", "ring", "pinky"]

            for i, finger in enumerate(finger_names):
                if finger in chords[hand_type]:
                    current_time = time.time()
                    center = hand["center"]

                    if fingers[i] == 1 and prev_states[hand_type][finger] == 0:
                        play_chord = chords[hand_type][finger]
                        for note in play_chord:
                            # Adjust velocity based on hand height (lower = louder)
                            hand_height = hand["center"][1]
                            height_ratio = max(0.2, min(1.0, (calibrated_height / hand_height)))
                            velocity = int(height_ratio * 127)
                            player.note_on(note, velocity)

                        latest_action[hand_type][finger] = current_time
                        cv2.putText(img, f"{finger.upper()} - {hand_type.upper()}",
                                    (center[0] + 10, center[1] + 30 * i),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        tip = hand["lmList"][i * 4][:2]
                        cv2.circle(img, tip, 10, (0, 255, 0), -1)

                    elif fingers[i] == 0 and prev_states[hand_type][finger] == 1:
                        chord_notes = chords[hand_type][finger]
                        threading.Thread(
                            target=stop_chord_after_delay,
                            args=(chord_notes, hand_type, finger, current_time),
                            daemon=True
                        ).start()
                        latest_action[hand_type][finger] = current_time

                    prev_states[hand_type][finger] = fingers[i]
    else:
        current_time = time.time()
        for hand_type in chords:
            for finger in chords[hand_type]:
                if prev_states[hand_type][finger] == 1:
                    chord_notes = chords[hand_type][finger]
                    threading.Thread(
                        target=stop_chord_after_delay,
                        args=(chord_notes, hand_type, finger, current_time),
                        daemon=True
                    ).start()
                    latest_action[hand_type][finger] = current_time
                prev_states[hand_type][finger] = 0

    # Draw the animated wave
    wave_phase += 10
    draw_wave(img, int(calibrated_height + 80), wave_phase)

    cv2.imshow("Hand Tracking MIDI Chords", img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('i'):
        for hand in chords:
            for finger in chords[hand]:
                for note in chords[hand][finger]:
                    player.note_off(note, 127)
        current_instrument_index = (current_instrument_index + 1) % len(instrument_keys)
        new_instrument = instrument_keys[current_instrument_index]
        player.set_instrument(new_instrument)
        print(f"🎼 Switched to: {instruments[new_instrument]}")

cap.release()
cv2.destroyAllWindows()
pygame.midi.quit()
