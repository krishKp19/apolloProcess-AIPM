def validate_input(data):
    if data["spo2"] < 0 or data["spo2"] > 100:
        return False
    return True