import bcrypt
import pytest


def _hash(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def test_hash_is_not_plaintext():
    pw = "securepass1"
    assert _hash(pw) != pw

def test_correct_password_verifies():
    pw = "correcthorsebattery"
    h = _hash(pw)
    assert bcrypt.checkpw(pw.encode(), h.encode())

def test_wrong_password_fails():
    pw = "correcthorsebattery"
    h = _hash(pw)
    assert not bcrypt.checkpw("wrongpassword".encode(), h.encode())

def test_empty_string_does_not_match_real_password():
    pw = "realpassword"
    h = _hash(pw)
    assert not bcrypt.checkpw(b"", h.encode())

def test_two_hashes_of_same_password_differ():
    pw = "samepassword"
    assert _hash(pw) != _hash(pw)

def test_hash_fits_database_column():
    # Schema uses VARCHAR(64); bcrypt output is 60 chars
    h = _hash("anypassword")
    assert len(h) <= 64
