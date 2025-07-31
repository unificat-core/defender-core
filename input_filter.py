def input_filter(user_input):
    blocked_words = ["fuck", "shit", "idiot", "kurwa", "jebac"]
    for word in blocked_words:
        if word in user_input.lower():
            return False
    return True
