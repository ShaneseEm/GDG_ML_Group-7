def validate_user_identifier(user_identifier: str, min_length: int = 3) -> tuple[bool, str]:
    cleaned_value = user_identifier.strip()

    if not cleaned_value:
        return False, "User name or ID is required before continuing."

    if len(cleaned_value) < min_length:
        return False, f"User name or ID must be at least {min_length} characters long."

    return True, "Valid"