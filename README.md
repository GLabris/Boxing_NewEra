# 🥊 Vision-Based Boxing Controller

A real-time computer vision system that detects and classifies boxing movements using pose estimation and maps them to virtual Xbox controller inputs.

Built with MediaPipe, OpenCV, and vgamepad.

---

## Overview

This project captures webcam input, extracts body landmarks, computes joint angles and motion dynamics, and translates physical boxing actions into in-game controller commands.

### Supported Interactions

- Straight  
- Hook  
- Uppercut  
- Body Hook  
- Blocking  
- Slipping  
- Lateral movement  

Each arm operates under a simple state machine:

`Guard → Extend → Retract`

Punch detection is validated using angle thresholds, motion velocity, and short temporal buffers for improved robustness.

---

## Tech Stack

- OpenCV  
- MediaPipe Pose  
- NumPy  
- vgamepad  

---
