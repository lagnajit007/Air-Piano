import cv2
import threading
import pygame.midi
import time
from cvzone.HandTrackingModule import HandDetector

# 🎹 Initialize Pygame MIDI
pygame.midi.init()
player = pygame.midi.Output(0)
player.set_instrument(0)  # 0 = Acoustic Grand Piano

# 🎐 Initialize Hand Detector
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8)

# 🎺 Chord Mapping for Fingers (D Major Scale)
chords = {
    "left": {
        "thumb": [50, 54, 57],   # D Major (D3, F#3, A3) - one octave lower
        "index": [52, 55, 59],   # E Minor (E3, G3, B3) - one octave lower
        "middle": [54, 57, 61],  # F# Minor (F#3, A3, C#4) - one octave lower
        "ring": [55, 59, 62],    # G Major (G3, B3, D4) - one octave lower
        "pinky": [57, 61, 64]    # A Major (A3, C#4, E4) - one octave lower
    },
    "right": {
        "thumb": [62, 66, 69],   # D Major (D4, F#, A)
        "index": [64, 67, 71],   # E Minor (E4, G, B)
        "middle": [66, 69, 73],  # F# Minor (F#4, A, C#)
        "ring": [67, 71, 74],    # G Major (G4, B, D)
        "pinky": [69, 73, 76]    # A Major (A4, C#, E)
    }
}

# Sustain Time (in seconds) after the finger is lowered
SUSTAIN_TIME = 2.0

# Track Previous States to Stop Chords
prev_states = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}

# Track the latest action timestamp for each finger to prevent overlapping
latest_action = {hand: {finger: 0 for finger in chords[hand]} for hand in chords}

# 🎵 Function to Play a Chord
def play_chord(chord_notes):
    for note in chord_notes:
        player.note_on(note, 127)  # Start playing

# 🎵 Function to Stop a Chord After a Delay
def stop_chord_after_delay(chord_notes, hand, finger, action_time):
    time.sleep(SUSTAIN_TIME)  # Sustain for specified time
    # Only stop the chord if this is the latest action for this finger
    if latest_action[hand][finger] == action_time:
        for note in chord_notes:
            player.note_off(note, 127)  # Stop playing

# Create a named window and set it to full screen
cv2.namedWindow("Hand Tracking MIDI Chords", cv2.WINDOW_NORMAL)

while True:
    success, img = cap.read()
    if not success:
        print("❌ Camera not capturing frames")
        continue
    
    # Flip the image horizontally
    img = cv2.flip(img, 1)

    hands, img = detector.findHands(img, draw=True)

    if hands:
        for hand in hands:
            hand_type = "left" if hand["type"] == "Left" else "right"
            fingers = detector.fingersUp(hand)
            finger_names = ["thumb", "index", "middle", "ring", "pinky"]

            for i, finger in enumerate(finger_names):
                if finger in chords[hand_type]:  # Only check assigned chords
                    current_time = time.time()  # Get current timestamp for this action
                    if fingers[i] == 1 and prev_states[hand_type][finger] == 0:
                        play_chord(chords[hand_type][finger])  # Play chord
                        latest_action[hand_type][finger] = current_time  # Update action time
                    elif fingers[i] == 0 and prev_states[hand_type][finger] == 1:
                        # Start a new thread to stop the chord, passing the action time
                        threading.Thread(
                            target=stop_chord_after_delay,
                            args=(chords[hand_type][finger], hand_type, finger, current_time),
                            daemon=True
                        ).start()
                        latest_action[hand_type][finger] = current_time  # Update action time
                    prev_states[hand_type][finger] = fingers[i]  # Update state
    else:
        # If no hands detected, stop all chords after delay
        current_time = time.time()
        for hand in chords:
            for finger in chords[hand]:
                if prev_states[hand][finger] == 1:
                    threading.Thread(
                        target=stop_chord_after_delay,
                        args=(chords[hand][finger], hand, finger, current_time),
                        daemon=True
                    ).start()
                    latest_action[hand][finger] = current_time
                prev_states[hand][finger] = 0  # Reset state

    cv2.imshow("Hand Tracking MIDI Chords", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.midi.quit()