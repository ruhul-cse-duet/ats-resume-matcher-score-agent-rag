from backend.app.auth import hash_password, verify_password

def test_password_hash_verify():
    pw = "secret123"
    h = hash_password(pw)
    assert verify_password(pw, h)
