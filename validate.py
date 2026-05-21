PLACEHOLDER = "YYYY-MM-DD"


def validate_patient_fields(patient_id, dob, doa, phone):
    """Return an error message string, or None when all fields are valid."""
    if not patient_id:
        return "Patient ID must have a value"
    if not patient_id.isdigit():
        return "Patient ID must be an integer"
    if dob in ("", PLACEHOLDER) or doa in ("", PLACEHOLDER):
        return "All date fields must be in YYYY-MM-DD format"
    if not phone.isdigit() or len(phone) != 10:
        return "Phone number must be 10 digits"
    return None
