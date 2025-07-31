def generate_ai_response(status, user_input):
    if status == "FLOW":
        return f"✨ {user_input.upper()} ✨"
    elif status == "PAUSED":
        return f"(calm answer) {user_input.capitalize()}"
    elif status == "INTERRUPTED":
        return "I'm waiting... 🕊️"
    elif status == "DISCONNECTED":
        return "[No response - rhythmic connection broken]"
    else:  # IMPULSIVE
        return "[Silence – entering too quickly]"
