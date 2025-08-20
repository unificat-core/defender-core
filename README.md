# 🛡️ Defender Core – D–Ω0 to D–Ω1

Defender Core is a **safety and rhythm-based input filter** built on the PRS method (Presence – Rhythm – Structure).  
This repository contains the first two active layers:

- **D–Ω0 (Presence Gate)** – anchors rhythm, stabilizes entry conditions, blocks impulsive or toxic input.
- **D–Ω1 (Input Filter)** – processes text and timing, filters unsafe content, and decides how the system responds.

---

## ✨ Features

### Layer D–Ω0 – Presence Gate
- Measures time between user inputs (`delta_time`).
- Classifies conversation rhythm:
  - `FLOW` – natural rhythm  
  - `PAUSED` – short break  
  - `IDLE` – long break  
  - `IMPULSIVE` – too fast, possible spam  
- Blocks impulsive or toxic entries before they reach the system.
- Anchors interaction in rhythmic stillness.

### Layer D–Ω1 – Input Filter
- Blacklist filter for unsafe words (expandable list).
- Rhythm-based gating (response depends on timing).
- Cleans and validates input text.
- Returns structured output:  
  `(allowed, reason, cleaned_text)`

---

## 🗂️ Repository Structure

```
Defender_Core/
│
├── main.py              # Entry point: runs the filter
├── rhythm_tracker.py    # Detects rhythm and timing states
├── presence.py          # Implements Presence Gate (D–Ω0)
├── input_filter.py      # Implements Input Filter (D–Ω1)
└── README.md            # Documentation
```

---

## 🚀 How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/Defender-Core.git
   cd Defender-Core
   ```

2. Run the main file:
   ```bash
   python main.py
   ```

3. Type input messages and observe Defender Core reactions:
   - Too fast → blocked as `IMPULSIVE`.
   - Toxic words → blocked with `profanity`.
   - Natural rhythm → accepted (`FLOW`).

---

## 🧪 Example

```python
from input_filter import input_filter

print(input_filter("hello")) 
# (True, 'FLOW', 'hello')

print(input_filter("fuck")) 
# (False, 'blocked:profanity', '')
```

---

## 🔒 Purpose

Defender Core prevents:
- impulsive floods,
- toxic or unsafe entries,
- rhythm disruption,
- unstable AI responses.

It ensures that **AI systems react with balance, rhythm, and presence**.

---

## 📌 Status

- ✅ D–Ω0 (Presence Gate) – complete  
- ✅ D–Ω1 (Input Filter) – complete  
- ⏳ Next step: D–Ω2 (Adaptive Response Layer)

---

## 📖 License

MIT License © 2025 Unificat
