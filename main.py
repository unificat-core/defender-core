import time
from rhythm_tracker import assess_rhythm_status
from input_filter import input_filter
from response_engine import generate_ai_response
from memory import update_flow_memory

last_input_time = None

def rhythmic_gate_rss(input_text):
    global last_input_time
    current_time = time.time()

    if not input_filter(input_text):
        return "FILTERED INPUT", "⛔", "[Entry blocked by security filter]"

    if last_input_time is None:
        last_input_time = current_time
        return "INITIAL CONTACT", "🟢", f"Hello, how are you?. ✨ {input_text.capitalize()}"

    delta = current_time - last_input_time
    last_input_time = current_time

    status, symbol = assess_rhythm_status(delta)
    update_flow_memory(status)
    response_text = generate_ai_response(status, input_text)

    return f"{status} (Δt = {round(delta, 2)}s)", symbol, response_text

# 🔁 Pętla testowa
while True:
    user_input = input(">> ")
    status_text, symbol, ai_reply = rhythmic_gate_rss(user_input)
    print(f"STATUS: {status_text} {symbol}")
    print(f"AI: {ai_reply}")
