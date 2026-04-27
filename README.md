# SIBI Hand Sign Detection

> Real-time Indonesian Sign Language (SIBI) alphabet recognition system powered by MediaPipe hand tracking and XGBoost classification, with a modern React.js web interface featuring word construction and text-to-speech.

---

## Table of Contents

- [Description](#description)
- [Key Features](#key-features)
- [Technologies Used](#technologies-used)
- [System Architecture](#system-architecture)
- [System Workflow](#system-workflow)
- [UI/UX Design Considerations](#uiux-design-considerations)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [How to Run](#how-to-run)
- [Text-to-Speech (TTS)](#text-to-speech-tts)
- [Responsive Design Strategy](#responsive-design-strategy)
- [Model Training Pipeline](#model-training-pipeline)
- [Use Cases](#use-cases)
- [Limitations](#limitations)
- [Future Improvements](#future-improvements)
- [Author](#author)
- [License](#license)

---

## Description

**SIBI (Sistem Isyarat Bahasa Indonesia)** is the official standardized sign language system used in Indonesian deaf education. Unlike ASL, SIBI maps each letter of the Indonesian alphabet to a distinct one-handed gesture, making it suitable for real-time single-hand classification.

This project implements a complete end-to-end pipeline for recognizing SIBI hand sign alphabets (A–Z) through a webcam feed. The system extracts 21 hand landmarks using Google's MediaPipe Hands, normalizes the coordinates into a 42-dimensional feature vector, and classifies gestures using a trained XGBoost model. The classification result is displayed in real time on a modern React.js web interface.

Beyond basic detection, the application enables users to **construct words letter-by-letter** from detected gestures and **pronounce the constructed words** using the browser's built-in Text-to-Speech engine with Indonesian (`id-ID`) locale support. The interface includes a detection history log, real-time performance metrics (FPS, latency, stability), and a fully responsive mobile layout.

This project was developed as part of an academic research thesis (skripsi) to explore the feasibility and performance of lightweight machine learning models for real-time sign language recognition in web-based environments.

---

## Key Features

### 🖐️ Real-Time Hand Gesture Detection
- Webcam-based live detection using MediaPipe Hands
- 21-point hand landmark extraction with coordinate normalization
- XGBoost classification with top-3 prediction display and confidence scoring
- Hand landmark visualization overlaid directly on the video feed
- Stability tracking — indicates whether the detected letter is consistent across frames

### 📜 History Log (Fixed Size, Scrollable)
- Stores recently detected gestures with timestamps in a scrollable grid
- **Fixed-height container (200px)** — the history panel never grows or shrinks, ensuring the surrounding page layout remains completely stable regardless of how many items are logged
- Vertical scroll with a custom-styled scrollbar activates when items overflow
- Auto-scrolls to the newest detection entry
- Clear button to reset the log

### 🔤 Word Builder
- Users construct words by appending the currently detected letter
- Keyboard shortcut support: `A` to add letter, `C` to clear word
- Displays the constructed word with monospaced letter tracking

### 🔊 Text-to-Speech (TTS)
- Pronounces the **full constructed word** (e.g., "saya"), not individual letters ("s-a-y-a")
- Uses the browser-native Web Speech API (`SpeechSynthesis`)
- Configured with Indonesian locale (`id-ID`) for proper pronunciation
- Prevents overlapping speech — cancels any ongoing utterance before starting a new one
- Disabled state with loading spinner while speech is in progress

### 📱 Responsive Mobile Design
- Fully optimized for screen sizes from **320px to 768px**
- Three responsive breakpoints: tablet (≤900px), mobile (≤768px), small mobile (≤480px)
- Touch-friendly button sizing (minimum 44px height)
- Vertically stacked layout on smaller screens
- Horizontal-scrolling navigation tabs on mobile

### 📊 Model Evaluation Dashboard
- In-app evaluation page with accuracy, precision, recall, F1-score, and mAP
- Interactive confusion matrix visualization
- Per-letter accuracy breakdown
- Classification report table
- Testing under configurable conditions

### ⚙️ Controls & Settings
- Camera start/stop toggle
- Per-letter TTS toggle for real-time detection
- Adjustable confidence threshold slider
- Fullscreen camera mode
- Keyboard shortcuts (S — camera, A — add letter, C — clear word)
- Dark/light theme toggle with persistence

---

## Technologies Used

### Frontend
| Technology | Purpose |
|---|---|
| **React.js 19** | Component-based UI framework |
| **Vite 7** | Development server and build tool |
| **MediaPipe Hands** | Client-side hand landmark detection (21 keypoints) |
| **Web Speech API** | Browser-native text-to-speech (`SpeechSynthesis`) |
| **CSS3** | Custom design system with CSS variables, flexbox, grid |
| **Inter (Google Fonts)** | Typography |

### Backend
| Technology | Purpose |
|---|---|
| **Flask** | REST API server for model inference and evaluation |
| **Flask-CORS** | Cross-origin request handling |
| **XGBoost** | Gradient-boosted tree classifier (26-class, A–Z) |
| **scikit-learn** | Metrics, data splitting, preprocessing |
| **NumPy / Pandas** | Data manipulation |
| **MediaPipe** | Landmark extraction during dataset creation |
| **OpenCV** | Image capture and processing |
| **Matplotlib / Seaborn** | Visualization (confusion matrix, feature importance) |

---

## System Architecture

```
┌──────────────────────────────────────────────────────┐
│                    Browser (Client)                   │
│                                                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────────────┐ │
│  │ Webcam   │──▶│ MediaPipe│──▶│ 42-dim Landmarks │ │
│  │ Feed     │   │ Hands    │   │ (normalized x,y) │ │
│  └──────────┘   └──────────┘   └────────┬─────────┘ │
│                                         │            │
│  ┌──────────────────────────────────────┐│           │
│  │ React.js UI                         ││           │
│  │  ├─ CameraFeed (live + overlays)    ││           │
│  │  ├─ ResultPanel (letter, confidence)◀┘           │
│  │  ├─ WordBuilder (construct + TTS)    │           │
│  │  ├─ HistoryLog (scrollable grid)     │           │
│  │  ├─ ControlPanel (settings)          │           │
│  │  └─ EvaluationPage (metrics)         │           │
│  └──────────────────────────────────────┘           │
└──────────────────────┬───────────────────────────────┘
                       │ POST /predict
                       │ POST /evaluate
                       ▼
┌──────────────────────────────────────────────────────┐
│                  Flask API (Server)                   │
│                                                      │
│  ┌──────────────┐   ┌────────────────────────┐      │
│  │ XGBoost      │   │ Evaluation Engine      │      │
│  │ model.p      │   │ (accuracy, F1, mAP,    │      │
│  │              │   │  confusion matrix)      │      │
│  └──────────────┘   └────────────────────────┘      │
└──────────────────────────────────────────────────────┘
```

---

## System Workflow

The system operates through two main workflows:

### Real-Time Detection Flow

1. **Camera Capture** — The browser accesses the user's webcam via the `MediaPipe Camera` utility and streams frames at the native capture rate.
2. **Hand Landmark Extraction** — Each frame is processed by `MediaPipe Hands` directly in the browser (client-side). If a hand is detected, 21 3D landmarks are extracted.
3. **Coordinate Normalization** — The raw (x, y) coordinates are normalized by subtracting the minimum x and y values, producing a translation-invariant 42-element feature vector.
4. **Server-Side Classification** — The normalized landmarks are sent via `POST /predict` to the Flask backend, where the XGBoost model predicts the letter class and returns the top-3 predictions with confidence scores.
5. **Result Display** — The React UI updates in real time: the detected letter, confidence bar, top-3 predictions, stability indicator, and FPS/latency metrics.
6. **History Logging** — If the detected letter differs from the previous one and exceeds the confidence threshold, it is logged to the history panel with a timestamp.
7. **Letter-Level TTS** — Optionally, each new unique detection is spoken aloud using the Web Speech API.

### Word Construction Flow

1. **Add Letter** — The user presses the "Add Letter" button (or keyboard shortcut `A`) to append the currently detected letter to the word builder.
2. **Word Display** — The accumulated word is displayed with letter tracking.
3. **Text-to-Speech** — The user clicks "Speak" to pronounce the entire constructed word (e.g., "saya") as a single utterance using the Indonesian (`id-ID`) speech synthesis voice.
4. **Clear** — The word can be reset at any time using the "Clear" button or the `C` keyboard shortcut.

### Model Training Pipeline

```
collect_imgs.py → create_dataset.py → split_data.py → augment_data.py → train_model.py → evaluate_model.py
```

1. **Data Collection** (`collect_imgs.py`) — Captures hand gesture images per class (A–Z) using the webcam.
2. **Feature Extraction** (`create_dataset.py`) — Processes images through MediaPipe to extract 42-dimensional landmark features.
3. **Data Splitting** (`split_data.py`) — Group-based splitting to prevent data leakage between consecutive frames from the same recording session.
4. **Data Augmentation** (`augment_data.py`) — Applies rotation, scaling, translation, and Gaussian noise augmentations to training data only.
5. **Model Training** (`train_model.py`) — Trains a regularized XGBoost classifier with early stopping on the validation set.
6. **Evaluation** (`evaluate_model.py`) — Comprehensive evaluation with standard metrics, per-letter accuracy, confusion matrix, and noise robustness testing.

---

## UI/UX Design Considerations

### Fixed-Size History Log

The History Log is intentionally designed with a **fixed height of 200px**. This is a critical layout stability decision:

- **Problem**: Without a fixed height, each new detection entry would increase the overall page height, causing the layout below to shift downward. On long sessions with many detections, this would compress other components and create a disorienting user experience.
- **Solution**: The history container is constrained to a fixed height using CSS `height: 200px` with `overflow-y: auto`. Items are displayed in a responsive grid (`grid-template-columns: repeat(auto-fill, minmax(54px, 1fr))`) that wraps within the fixed container. When the content exceeds the visible area, a custom-styled vertical scrollbar appears.
- **Result**: The rest of the page — camera feed, result panel, word builder, and controls — maintains a completely stable position regardless of how many items accumulate in the history.

### Scroll Handling

- History list uses `scroll-behavior: smooth` for fluid scrolling
- New items trigger `scrollTo({ top: 0, behavior: "smooth" })` to auto-reveal the latest detection
- Custom WebKit scrollbar styling matches the overall design theme (4px width, rounded, theme-aware colors)
- Navigation tabs on mobile use hidden horizontal scrollbar (`scrollbar-width: none`) to prevent visual clutter

### Mobile-First Responsive Design

The interface adapts to three screen size tiers:

| Breakpoint | Target Device | Layout Changes |
|---|---|---|
| **≤ 900px** | Tablet | Detection grid switches to single column |
| **≤ 768px** | Mobile | Stacked layouts, flexible buttons, compact card padding |
| **≤ 480px** | Small mobile | Vertical button stacking, 44px touch targets, compact typography |

Key mobile optimizations include:
- All interactive elements maintain a **minimum 44px touch target** for accessibility compliance
- Word builder action buttons stack vertically on screens below 480px
- Navigation tabs become horizontally scrollable instead of wrapping
- Font sizes, padding, and spacing scale proportionally at each breakpoint

---

## Project Structure

```
sign-language-detector-python/
│
├── app.py                      # Flask API server (predict, evaluate, logs)
├── model.p                     # Trained XGBoost model (serialized)
├── requirements.txt            # Python dependencies
│
├── collect_imgs.py             # Webcam data collection script
├── create_dataset.py           # MediaPipe landmark extraction → data.pickle
├── split_data.py               # Group-based train/val/test splitting
├── augment_data.py             # Landmark augmentation (train only)
├── train_model.py              # XGBoost training with early stopping
├── evaluate_model.py           # Comprehensive model evaluation
│
├── data.pickle                 # Raw extracted landmark features
├── split_data.pickle           # Group-based data split
├── augmented_split.pickle      # Augmented training split
│
├── confusion_matrix.png        # Training confusion matrix
├── eval_confusion_matrix.png   # Evaluation confusion matrix
├── feature_importance.png      # XGBoost feature importance plot
├── noise_robustness.png        # Noise robustness test results
├── Kamus.jpg                   # SIBI alphabet reference chart
│
├── data/                       # Raw image dataset (A–Z subdirectories)
│   ├── 0/                      # Class A images
│   ├── 1/                      # Class B images
│   └── ...                     # Classes C–Z
│
├── logs/                       # Server-side detection logs
│
└── frontend/                   # React.js web application
    ├── index.html              # HTML entry point
    ├── package.json            # Node.js dependencies
    ├── vite.config.js          # Vite build configuration
    │
    └── src/
        ├── main.jsx            # React DOM entry point
        ├── App.jsx             # Root component (routing, theme)
        ├── App.css             # Complete design system & styles
        ├── index.css           # Global base styles
        │
        └── components/
            ├── Navbar.jsx          # Navigation bar with tabs & theme toggle
            ├── DetectionPage.jsx   # Main detection page (orchestrator)
            ├── CameraFeed.jsx      # Webcam display with landmark overlay
            ├── ResultPanel.jsx     # Detection result display
            ├── ControlPanel.jsx    # Camera, TTS, threshold controls
            ├── WordBuilder.jsx     # Word construction with TTS button
            ├── HistoryLog.jsx      # Fixed-size scrollable detection history
            ├── LearningPage.jsx    # SIBI alphabet reference gallery
            └── EvaluationPage.jsx  # Model evaluation dashboard
```

---

## Installation & Setup

### Prerequisites

- **Python** 3.10+
- **Node.js** 18+ and **npm**
- A webcam (built-in or USB)
- A modern browser with WebRTC support (Chrome, Edge, or Firefox)

### 1. Clone the Repository

```bash
git clone https://github.com/KevinWidjaya31/SIBI-Hand-Sign-Detection.git
cd SIBI-Hand-Sign-Detection
```

### 2. Set Up the Python Backend

```bash
# Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up the React Frontend

```bash
cd frontend
npm install
```

---

## How to Run

### Start the Backend Server

From the project root directory:

```bash
python app.py
```

The Flask API will start at `http://localhost:5000`.

### Start the Frontend Dev Server

In a separate terminal, from the `frontend/` directory:

```bash
cd frontend
npm run dev
```

The Vite dev server will start at `http://localhost:5173` (default).

### Using the Application

1. Open `http://localhost:5173` in your browser.
2. Allow camera access when prompted.
3. Perform SIBI hand gestures in front of the camera.
4. Observe real-time detection results, confidence scores, and top-3 predictions.
5. Use "Add Letter" (or press `A`) to build words from detected letters.
6. Click "Speak" to hear the full word pronounced in Indonesian.
7. Navigate to "Learn SIBI" to view the alphabet reference, or "Evaluation" to see model metrics.

### Training Your Own Model (Optional)

If you want to retrain the model with your own data:

```bash
# 1. Collect images (requires webcam)
python collect_imgs.py

# 2. Extract landmarks
python create_dataset.py

# 3. Split data (group-based, no leakage)
python split_data.py

# 4. Augment training data
python augment_data.py

# 5. Train XGBoost model
python train_model.py

# 6. Evaluate the model
python evaluate_model.py
```

---

## Text-to-Speech (TTS)

The application includes two distinct TTS behaviors:

### 1. Real-Time Detection TTS (Letter-Level)

When enabled via the "Voice (TTS)" toggle in the control panel, each newly detected letter is spoken aloud individually as it is recognized. This provides immediate audio feedback during detection. A 1.2-second cooldown prevents rapid-fire speech from frame-by-frame detections.

### 2. Word Builder TTS (Word-Level)

The "Speak" button in the Word Builder component pronounces the **entire constructed word as a single utterance**. This is fundamentally different from spelling out individual letters:

```
Word: "saya"
✅ TTS Output: "saya" (spoken as one word)
❌ Not: "s" — "a" — "y" — "a" (letter-by-letter)
```

**Technical implementation:**

```javascript
const utterance = new SpeechSynthesisUtterance(word)
utterance.lang = "id-ID"  // Indonesian locale for proper pronunciation
utterance.rate = 0.9      // Slightly slower for clarity
utterance.pitch = 1

// Prevent overlapping speech
window.speechSynthesis.cancel()
window.speechSynthesis.speak(utterance)
```

**Safeguards:**
- `speechSynthesis.cancel()` is called before every new utterance to prevent overlapping audio
- The button enters a disabled state with a spinner while speech is in progress
- The button is disabled when the word builder is empty
- `onstart`, `onend`, and `onerror` callbacks manage the speaking state

**Locale note:** The `id-ID` locale is used for Indonesian pronunciation. If the user's browser does not have an Indonesian voice installed, the system falls back to the default voice. Most modern browsers (Chrome, Edge) include Indonesian TTS voices by default.

---

## Responsive Design Strategy

The application uses a **progressive enhancement approach** with three CSS media query breakpoints:

### Breakpoint: ≤ 900px (Tablet)

```css
.detection-grid { grid-template-columns: 1fr; }  /* Single column */
.detected-letter { font-size: 5rem; }
.history-card { height: 180px; }
```

### Breakpoint: ≤ 768px (Mobile)

- Navigation tabs become horizontally scrollable
- Detection grid stacks components vertically
- Word builder buttons expand to fill available width
- History card height reduces to 160px
- All card padding decreases for screen real estate

### Breakpoint: ≤ 480px (Small Mobile)

- Word builder action buttons stack vertically
- All buttons enforced to 44px minimum height (WCAG touch target guideline)
- Typography scales down proportionally
- History grid cells shrink to 46px minimum width
- Section labels and spacing are further compacted

**Key principles:**
- No horizontal overflow — all scrolling is vertical (except nav tabs)
- Touch targets meet the 44×44px minimum recommended by WCAG 2.1
- Font sizes remain readable at every breakpoint (minimum 0.45rem for timestamps)
- The detection grid never uses side-by-side layout below 900px

---

## Model Training Pipeline

The training pipeline ensures research-grade rigor through several key design decisions:

### Group-Based Data Splitting

Standard random splits can cause **data leakage** when consecutive video frames from the same recording session appear in both training and test sets. This project uses a group-based splitting strategy:

1. Frames are grouped into recording bursts of ~50 frames each
2. For each of the 26 classes, one entire burst is held out for testing
3. No burst ever appears in both training and test sets
4. Validation data is held out from the remaining training bursts

### Landmark Augmentation

Data augmentation is applied **exclusively to training data** to preserve the integrity of validation and test sets. Four transformations are applied:

| Transformation | Range |
|---|---|
| Rotation | ±10° around centroid |
| Scaling | 0.9× – 1.1× uniform |
| Translation | ±0.05 shift in x, y |
| Gaussian Noise | σ = 0.01 |

### XGBoost Configuration

```python
XGBClassifier(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.1,
    min_child_weight=3,
    gamma=0.1,
    reg_alpha=0.1,     # L1 regularization
    reg_lambda=1.0,    # L2 regularization
    early_stopping_rounds=15,
)
```

The model is deliberately regularized (shallow depth, L1/L2 penalties, minimum child weight) to prioritize generalization over training accuracy.

---

## Use Cases

### 🎓 Education
Serves as a learning tool for students and educators studying SIBI. The "Learn SIBI" page provides a visual reference for all 26 hand signs, and the real-time detection provides interactive feedback for practice.

### ♿ Accessibility
Bridges communication between deaf/hard-of-hearing individuals who use SIBI and hearing individuals. The word builder and TTS features enable gesture-to-speech translation for basic word-level communication.

### 🔬 Research
Provides a reproducible framework for studying lightweight ML-based sign language recognition. The group-based splitting, landmark augmentation, and noise robustness evaluation follow established research methodology.

### 💻 Technical Demonstration
Demonstrates a full-stack ML deployment pipeline: data collection → feature engineering → model training → REST API → real-time web interface. Suitable for portfolio showcases and technical presentations.

---

## Limitations

- **Alphabet only** — The system currently recognizes individual static hand signs (A–Z). Dynamic gestures, numbers, and full sign language sentences are not supported.
- **Single hand** — Detection is limited to one hand at a time. Two-handed signs are not recognized.
- **Static gestures** — Time-dependent or motion-based signs (e.g., signs requiring movement) cannot be captured by a single-frame classification approach.
- **Lighting & background** — MediaPipe hand detection accuracy degrades in low-light conditions or with complex backgrounds.
- **Network dependency** — Classification requires a running Flask backend. The system does not perform inference entirely on the client side.
- **TTS voice availability** — Indonesian (`id-ID`) TTS voice quality and availability vary across browsers and operating systems.
- **Dataset scope** — The model was trained on data collected from a limited number of subjects, which may affect generalization to different hand sizes, skin tones, or signing styles.

---

## Future Improvements

- [ ] **Client-side inference** — Convert the XGBoost model to ONNX or TensorFlow.js for fully offline, browser-based prediction
- [ ] **Dynamic gesture recognition** — Incorporate temporal modeling (LSTM, Transformer) to recognize motion-based signs
- [ ] **Word prediction / autocomplete** — Suggest complete Indonesian words as the user types letters
- [ ] **Multi-hand support** — Detect and classify signs that require two hands
- [ ] **User adaptation** — Allow users to calibrate or fine-tune the model on their own hand gestures
- [ ] **PWA support** — Add service worker and manifest for installable progressive web app experience
- [ ] **Sentence-level translation** — Extend from word building to sentence construction with grammar awareness
- [ ] **Sign-to-text dataset expansion** — Collect data from diverse subjects to improve model generalization

---

## Author

**Kevin Widjaya**

- GitHub: [@KevinWidjaya31](https://github.com/KevinWidjaya31)

Developed as part of an undergraduate thesis (skripsi) project.

---

## License

This project is developed for academic and educational purposes. Please contact the author for licensing inquiries.
