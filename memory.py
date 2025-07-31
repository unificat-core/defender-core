last_status = None

def update_flow_memory(current_status):
    global last_status
    last_status = current_status

def get_last_status():
    return last_status
