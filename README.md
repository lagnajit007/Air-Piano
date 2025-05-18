# Air-Piano🎹:

Control MIDI piano chords in real-time using hand gestures captured from your webcam. Each finger is mapped to a chord in the D major scale, with the left hand playing in a lower octave for a richer sound. Chords play and sustain naturally as you move your fingers, with thread-safe handling to prevent overlapping notes.

---

## 📦 Features

- 🖐️ Real-time hand detection using [cvzone](https://github.com/cvzone/cvzone)
- 🎼 Chord mapping to fingers in the D major scale, with lower octaves for the left hand
- 🎹 MIDI output with sustain effect using `pygame.midi`
- 👏 Supports both left and right hands with distinct octave ranges
- 🎶 Thread-safe chord transitions to prevent note overlaps
- 🚀 Dynamic gesture-based music interaction

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/lagnajit007/Air-Piano.git

```

### 2. Install Dependencies

Make sure Python 3.7+ is installed.

```bash
pip install opencv-python pygame cvzone
```

> If `cvzone` is not found, install directly from GitHub:
```bash
pip install git+https://github.com/cvzone/cvzone.git
```

---

## 🎛️ How It Works

- The webcam detects your hands in real-time using `cvzone`’s `HandDetector`.
- Each finger corresponds to a specific chord, with the left hand playing chords one octave lower than the right hand for a fuller sound.
- When a finger is raised (`fingersUp`), the corresponding chord is played.
- When the finger is lowered, the chord sustains for a configurable delay before stopping.
- A thread-safe mechanism using timestamps ensures smooth chord transitions, preventing overlaps from rapid finger movements.

### 🎵 Chord Mapping (D Major Scale)

#### Left Hand (Lower Octave)
| Finger  | Chord (MIDI Notes)   | Description        |
|---------|----------------------|--------------------|
| Thumb   | D Major (50, 54, 57) | D3 - F#3 - A3      |
| Index   | E Minor (52, 55, 59) | E3 - G3 - B3       |
| Middle  | F# Minor (54, 57, 61)| F#3 - A3 - C#4     |
| Ring    | G Major (55, 59, 62) | G3 - B3 - D4       |
| Pinky   | A Major (57, 61, 64) | A3 - C#4 - E4      |

#### Right Hand
| Finger  | Chord (MIDI Notes)   | Description        |
|---------|----------------------|--------------------|
| Thumb   | D Major (62, 66, 69) | D4 - F#4 - A4      |
| Index   | E Minor (64, 67, 71) | E4 - G4 - B4       |
| Middle  | F# Minor (66, 69, 73)| F#4 - A4 - C#5     |
| Ring    | G Major (67, 71, 74) | G4 - B4 - D5       |
| Pinky   | A Major (69, 73, 76) | A4 - C#5 - E5      |

---

## 🧠 Code Overview

- `pygame.midi.init()` initializes MIDI output.
- `cvzone.HandTrackingModule.HandDetector` handles hand and finger tracking.
- `fingersUp()` determines which fingers are raised.
- MIDI notes are triggered with `note_on` and `note_off` functions.
- Chords are sustained for a configurable delay (`SUSTAIN_TIME = 2.0`).
- Timestamps (`latest_action`) ensure only the latest chord action is processed, preventing overlaps from rapid gestures.

---

## 💡 Customization

- 🔁 **Change Instrument**:  
  Modify the instrument using:
  ```python
  player.set_instrument(<instrument_number>)
  ```
  Refer to the [General MIDI Instrument List](https://www.midi.org/specifications-old/item/gm-level-1-sound-set) for codes.

- 🎼 **Change Chord Scale**:  
  Replace the `chords` dictionary with your preferred scales or custom mappings. Adjust MIDI note numbers for different octaves or chords.

- ⏱️ **Adjust Sustain Time**:  
  Modify `SUSTAIN_TIME` (in seconds) to lengthen or shorten the delay after chord release:
  ```python
  SUSTAIN_TIME = 2.0  # Adjust as needed
  ```

- 🎹 **Octave Adjustments**:  
  Modify the MIDI note numbers in the `chords` dictionary to shift octaves (e.g., subtract/add 12 for one octave lower/higher).

---

## 🛑 Exit Instructions

- Press `q` on your keyboard to quit the application safely.
- This releases the webcam and MIDI resources.



## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---