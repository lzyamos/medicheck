def evaluate_urgency(symptoms: list[dict]) -> str:
    # Simple, explicit red-flag rules (expandable)
    for s in symptoms:
        name = s["symptom"].lower()
        severity = s["severity"]
        days = s["duration_days"]

        if "chest pain" in name and severity >= 7:
            return "URGENT"
        if "shortness of breath" in name and severity >= 7:
            return "URGENT"
        if "loss of consciousness" in name:
            return "URGENT"
        if "fever" in name and severity >= 8 and days >= 3:
            return "PROMPT"

    return "ROUTINE"


def condition_insights(symptoms: list[dict]) -> list[dict]:
    insights = []
    names = " ".join([s["symptom"].lower() for s in symptoms])

    if "fever" in names and "cough" in names:
        insights.append({
            "condition": "Respiratory infection",
            "confidence": "Low",
            "note": "Based on symptom clustering; not diagnostic."
        })

    if "abdominal pain" in names:
        insights.append({
            "condition": "Gastrointestinal condition",
            "confidence": "Low",
            "note": "Broad category; requires further evaluation."
        })

    if not insights:
        insights.append({
            "condition": "Non-specific symptoms",
            "confidence": "Low",
            "note": "Insufficient specificity for targeted insight."
        })

    return insights


def recommended_tests(symptoms: list[dict]) -> list[dict]:
    tests = []
    names = " ".join([s["symptom"].lower() for s in symptoms])

    if "fever" in names:
        tests.append({"test": "Complete Blood Count (CBC)", "reason": "Assess infection or inflammation."})

    if "cough" in names or "shortness of breath" in names:
        tests.append({"test": "Chest X-ray", "reason": "Evaluate lung pathology."})

    if "abdominal pain" in names:
        tests.append({"test": "Abdominal Ultrasound", "reason": "Evaluate abdominal organs."})

    return tests
