def assess_rhythm_status(delta_time):
    if delta_time < 1.0:
        return "IMPULSIVE", "🔴"
    elif delta_time < 3.0:
        return "FLOW", "🟢"
    elif delta_time < 10.0:
        return "PAUSED", "🟡"
    elif delta_time < 60.0:
        return "INTERRUPTED", "🟠"
    else:
        return "DISCONNECTED", "⚫"
