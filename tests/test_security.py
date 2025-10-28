"""Tests for security validation functionality."""
from app.security import security_validator

def test_validate_input_clean():
    text = "Hello world! This is a normal text input."
    is_valid, issues = security_validator.validate_input(text)
    assert is_valid
    assert not issues

def test_validate_input_script_injection():
    text = "Hello <script>alert('xss')</script>"
    is_valid, issues = security_validator.validate_input(text)
    assert not is_valid
    assert "suspicious_pattern_detected" in issues

def test_validate_input_sql_injection():
    text = "SELECT * FROM users; DROP TABLE users;"
    is_valid, issues = security_validator.validate_input(text)
    assert not is_valid
    assert "suspicious_pattern_detected" in issues

def test_validate_input_command_injection():
    text = "hello; rm -rf /"
    is_valid, issues = security_validator.validate_input(text)
    assert not is_valid
    assert "command_injection_risk" in issues

def test_validate_input_special_chars():
    text = "!@#$%^&*())))~~~{{{}}}"
    is_valid, issues = security_validator.validate_input(text)
    assert not is_valid
    assert "excessive_special_chars" in issues

def test_validate_api_key_valid():
    api_key = "abcd1234efgh5678ijkl9012mnop3456"
    is_valid, issues = security_validator.validate_api_key(api_key)
    assert is_valid
    assert not issues

def test_validate_api_key_too_short():
    api_key = "short_key"
    is_valid, issues = security_validator.validate_api_key(api_key)
    assert not is_valid
    assert "api_key_too_short" in issues

def test_validate_api_key_invalid_format():
    api_key = "invalid*key*with*special*chars!"
    is_valid, issues = security_validator.validate_api_key(api_key)
    assert not is_valid
    assert "api_key_invalid_format" in issues

def test_validate_api_key_sequential():
    api_key = "abcd1111efghijklmnopqrstuvwxyz1234"
    is_valid, issues = security_validator.validate_api_key(api_key)
    assert not is_valid
    assert "api_key_sequential_pattern" in issues