# DEFENDER CORE – Layer D–Ω0 (v0.2)

## Purpose:
Layer D–Ω0 acts as a rhythmic input gate, protecting the AI system from:
- impulsive entries (too fast),
- toxic entries (blocked words),
- disruption of interaction rhythm (gaps, chaos),
- unstable responses (adaptive reaction form based on timing).

## Features:
- Measures time between user inputs (`delta_time`)
- Classifies rhythmic status: FLOW, PAUSED, INTERRUPTED, DISCONNECTED, IMPULSIVE
- Filters content for blocked/unsafe words
- Generates AI responses depending on rhythmic status
- Silences or modifies responses based on timing or content

## How to Run:
```bash
python main.py
```

## File Structure:
- `main.py` – main loop and interface
- `rhythm_tracker.py` – rhythm classification logic
- `input_filter.py` – basic word-level safety filter
- `response_engine.py` – AI reply generation
- `memory.py` – stores last status (optional but included)

## Status:
✅ Stable MVP version of Layer D–Ω0  
🟢 Ready for integration with LLMs or expansion into D–Ω1
