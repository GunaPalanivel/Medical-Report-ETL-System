def validate_age(value: int) -> bool:
    return 0 <= value <= 120


def validate_bmi(value: float) -> bool:
    return 0.0 <= value <= 100.0
