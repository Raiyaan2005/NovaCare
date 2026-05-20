import pytest
from validate import validate_patient_fields


def test_all_valid_fields_pass():
    assert validate_patient_fields("42", "2000-01-01", "2024-06-15", "0123456789") is None


# ── Patient ID ────────────────────────────────────────────────────────────────

def test_empty_patient_id_rejected():
    assert validate_patient_fields("", "2000-01-01", "2024-06-15", "0123456789") is not None

def test_alphabetic_patient_id_rejected():
    assert validate_patient_fields("abc", "2000-01-01", "2024-06-15", "0123456789") is not None

def test_alphanumeric_patient_id_rejected():
    # Previously "123abc" passed the old substring check — this confirms the fix
    assert validate_patient_fields("123abc", "2000-01-01", "2024-06-15", "0123456789") is not None

def test_single_letter_patient_id_rejected():
    assert validate_patient_fields("a", "2000-01-01", "2024-06-15", "0123456789") is not None

def test_numeric_string_patient_id_accepted():
    assert validate_patient_fields("1", "2000-01-01", "2024-06-15", "0123456789") is None


# ── Dates ─────────────────────────────────────────────────────────────────────

def test_placeholder_dob_rejected():
    assert validate_patient_fields("1", "YYYY-MM-DD", "2024-06-15", "0123456789") is not None

def test_empty_dob_rejected():
    assert validate_patient_fields("1", "", "2024-06-15", "0123456789") is not None

def test_placeholder_doa_rejected():
    assert validate_patient_fields("1", "2000-01-01", "YYYY-MM-DD", "0123456789") is not None

def test_empty_doa_rejected():
    assert validate_patient_fields("1", "2000-01-01", "", "0123456789") is not None


# ── Phone number ──────────────────────────────────────────────────────────────

def test_nine_digit_phone_rejected():
    assert validate_patient_fields("1", "2000-01-01", "2024-06-15", "012345678") is not None

def test_eleven_digit_phone_rejected():
    assert validate_patient_fields("1", "2000-01-01", "2024-06-15", "01234567890") is not None

def test_exact_ten_digit_phone_accepted():
    assert validate_patient_fields("1", "2000-01-01", "2024-06-15", "0123456789") is None
