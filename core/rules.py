def rule_engine(data):
    flags = []

    if data["spo2"] < 92:
        flags.append("low_oxygen")

    if "chest pain" in data["symptoms"]:
        flags.append("cardiac_risk")

    if data["hr"] > 110:
        flags.append("tachycardia")

    return flags