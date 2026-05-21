import pytest
from records import filter_rows, sort_rows

# 12-column sample rows matching the treeview column order (no Date of Birth)
ROWS = [
    ("1",  "Dr. Smith", "Cardiology", "Alice Brown", "F", "123 Main St", 34, "Blue Cross", "A+",  "5551234567", "120/80", "2024-06-01"),
    ("2",  "Dr. Jones", "Neurology",  "Bob White",   "M", "456 Oak Ave",  39, "Aetna",      "O-",  "5559876543", "110/70", "2024-07-15"),
    ("3",  "Dr. Smith", "Cardiology", "Carol Black", "F", "789 Pine Rd",  24, "Blue Cross", "B+",  "5550001111", "130/85", "2024-08-20"),
    ("10", "Dr. Lee",   "Pediatrics", "Dan Green",   "M", "321 Elm St",   14, "Cigna",      "AB+", "5552223333", "90/60",  "2024-09-05"),
]


# ── filter_rows ───────────────────────────────────────────────────────────────

def test_empty_term_returns_all_rows():
    assert filter_rows(ROWS, "") == list(ROWS)

def test_filter_by_exact_name():
    result = filter_rows(ROWS, "alice brown")
    assert len(result) == 1 and result[0][3] == "Alice Brown"

def test_filter_by_partial_name():
    result = filter_rows(ROWS, "bob")
    assert len(result) == 1 and result[0][3] == "Bob White"

def test_filter_by_department_matches_multiple():
    assert len(filter_rows(ROWS, "cardiology")) == 2

def test_filter_is_case_insensitive():
    assert filter_rows(ROWS, "NEUROLOGY") == filter_rows(ROWS, "neurology")

def test_filter_by_doctor_name():
    result = filter_rows(ROWS, "dr. smith")
    assert len(result) == 2

def test_filter_no_match_returns_empty():
    assert filter_rows(ROWS, "zzznomatch") == []

def test_filter_does_not_mutate_input():
    original = list(ROWS)
    filter_rows(ROWS, "cardiology")
    assert list(ROWS) == original


# ── sort_rows ─────────────────────────────────────────────────────────────────

def test_sort_by_name_ascending():
    result = sort_rows(ROWS, col_idx=3, ascending=True)
    names = [r[3] for r in result]
    assert names == sorted(names, key=str.lower)

def test_sort_by_name_descending():
    result = sort_rows(ROWS, col_idx=3, ascending=False)
    names = [r[3] for r in result]
    assert names == sorted(names, key=str.lower, reverse=True)

def test_sort_patient_id_is_numeric_not_lexicographic():
    # Lexicographic order would give 1, 10, 2, 3 — numeric gives 1, 2, 3, 10
    result = sort_rows(ROWS, col_idx=0, ascending=True)
    ids = [int(r[0]) for r in result]
    assert ids == sorted(ids)

def test_sort_patient_id_descending():
    result = sort_rows(ROWS, col_idx=0, ascending=False)
    ids = [int(r[0]) for r in result]
    assert ids == sorted(ids, reverse=True)

def test_sort_does_not_mutate_input():
    original = list(ROWS)
    sort_rows(ROWS, col_idx=3, ascending=True)
    assert list(ROWS) == original
