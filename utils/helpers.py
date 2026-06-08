from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password):
    return generate_password_hash(password)


def verify_password(password, hashed):
    return check_password_hash(hashed, password)


def calculate_performance(scores):
    """Return (avg_score, performance_label) from a list of numeric scores."""
    if not scores:
        return 0, "No data"
    avg = sum(scores) / len(scores)
    if avg >= 8:
        label = "Excellent"
    elif avg >= 6:
        label = "Good"
    elif avg >= 4:
        label = "Average"
    else:
        label = "Needs Improvement"
    return round(avg, 1), label
