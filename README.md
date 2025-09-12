#AirClass – Touchless Interactive Learning for Everyone

AirClass is an **AI-powered, gesture-controlled educational platform** designed to make learning **inclusive, engaging, and accessible**, especially for **physically challenged learners**.  
It uses **computer vision, hand tracking, and gesture-based interaction** to create a fully **touchless classroom experience** where learners interact with lessons by moving their hands in the air.  

---

## ✨ Key Features

- 🎥 **Camera Overlay UI** – Live camera feed with interactive buttons and elements drawn on top.  
- ✋ **Hand Tracking & Gesture Control** – Pinch, swipe, and hover to interact with lessons.  
- 📚 **Learning Modules**
  - **Shapes & Colors** – Learn to recognize, identify, and interact with different shapes and colors.  
  - **Numbers** – Counting, addition, subtraction, multiplication, division, odd/even, fill-in-the-missing, and tracing.  
  - **Spellings** – Interactive spelling practice with letter selection, hints, lives, and pronunciation.  
  - **Drawing** – Draw shapes and numbers using hand gestures.  
- 🔊 **Audio-Visual Feedback** – Sounds, animations, and on-screen prompts for engagement.  
- 🎨 **Nickelodeon-style UI** – Flashy, colorful, and kid-friendly interface.  
- ♿ **Inclusive Design** – Built for physically challenged learners with **hands-free interaction**.  

---

## 📂 Project Structure

```
AirClass/
│
├── main.py              # Main entry point (menu + shared resources)
├── graphics.py          # Rendering utilities (buttons, overlays, UI elements)
├── hand_tracker.py      # Mediapipe-based hand tracking
│
├── modules/             # All learning modules
│   ├── shapes_colors.py
│   ├── numbers.py
│   ├── spellings.py
│   └── drawing.py
│
├── assets/              # Sounds, icons, animations
│   ├── sounds/
│   ├── icons/
│   └── tutor/
│
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
```

---

## 🖥️ Installation Guide (Windows)

Follow these steps to set up and run AirClass on **Windows**:

### 1. Clone the Repository
```bash
git clone https://github.com/Veolinan/Airclass.git
cd Airclass
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
```bash
venv\Scriptsctivate
```
You should see `(venv)` before your command prompt.

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Run the Application
```bash
python main.py
```

---

## 🎮 Usage

Launch `main.py` and use your hand in front of the webcam to interact:

- ✋ **Pinch (index + thumb)** to select items  
- ⏳ **Hover & Hold** on menu buttons to open a module  
- 🔙 **Back button** inside modules to return to main menu  
- 🔊 Follow on-screen **audio + visual prompts**  

---

## 🔧 Dependencies

- OpenCV – Camera & image processing  
- Mediapipe – Hand tracking  
- Pygame – UI, sound, graphics  
- TensorFlow Lite Runtime – For gesture model inference (optional AI integration)  
- All dependencies are listed in `requirements.txt`.  

---

## 🌍 Vision & Impact

AirClass is more than a project – it’s a step towards inclusive education.  
By enabling hands-free, gesture-based learning, it ensures that physically challenged learners can participate in interactive lessons without barriers.  

---

## 🤝 Contributing

We welcome contributions!

1. Fork the repo  
2. Create a feature branch  
3. Submit a PR 🚀  

---

## 📜 License

MIT License – free to use, modify, and share.  
