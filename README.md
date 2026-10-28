 # Virtual Hand Mouse 🖐️

## Project Overview
Virtual Hand Mouse is a Python-based application that uses a webcam and hand gesture recognition to control the computer mouse without physically touching a mouse.

## Features

- Control the mouse cursor using hand movements.
- Perform single-click and double-click actions using finger gestures.
- Scroll pages using hand gestures.
- Capture screenshots using a hand gesture.
- Track hand movements using a webcam.

## Technologies Used

- Python
- OpenCV
- MediaPipe
- NumPy
- PyAutoGUI

## How It Works

1. The webcam captures live video.
2. MediaPipe detects and tracks hand landmarks.
3. The program identifies specific hand gestures.
4. PyAutoGUI performs mouse actions based on the detected gestures.

## Requirements

- Python 3.11
- A working webcam
- The Python libraries listed in `requirements.txt`

## Installation

### 1. Clone the repository
Replace `YOUR_USERNAME` with your GitHub username.

```bash
git clone https://github.com/YOUR_USERNAME/Virtual-Hand-Mouse.git
```

### 2. Open the project folder

```bash
cd Virtual-Hand-Mouse
```

### 3. Install the required libraries

```bash
python -m pip install -r requirements.txt
```

### 4. Run the program
Replace `main.py` with your actual Python filename if it is different.

```bash
python main.py
```

## Controls

- **Index finger movement:** Move the mouse cursor.
- **Pinch thumb and index finger:** Perform a click.
- **Quick repeated pinch:** Perform a double-click.
- **Raise all four fingers other than the thumb:** Activate scrolling.
- **Three-finger pinch gesture:** Trigger the screenshot action, as implemented in the current code.
- **Q key:** Exit the application.

## Project Structure

```
VirtualHandMouse/
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```
*Note: Replace `main.py` with your actual Python script filename if necessary.*

## Future Improvements

- Add more customizable hand gestures.
- Improve cursor accuracy and smoothness.
- Add a graphical user interface.
- Improve gesture recognition in different lighting conditions.

## Learning Outcomes
This project demonstrates the practical use of computer vision, hand landmark detection, Python programming, and mouse automation.

## Author
Suhas D
