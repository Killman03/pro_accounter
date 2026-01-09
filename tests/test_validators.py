import pytest
from utils.validators import validate_kg_phone


class TestValidateKgPhone:
    """Тесты для валидации киргизских телефонных номеров"""
    
    def test_valid_phone_starts_with_996(self):
        """Тест валидного номера начинающегося с 996"""
        assert validate_kg_phone("996555123456") is True
    
    def test_valid_phone_10_digits_after_996(self):
        """Тест валидного номера с 10 цифрами после 996"""
        assert validate_kg_phone("996123456789") is True
    
    def test_invalid_phone_too_short(self):
        """Тест невалидного номера - слишком короткий"""
        assert validate_kg_phone("99655512345") is False
    
    def test_invalid_phone_too_long(self):
        """Тест невалидного номера - слишком длинный"""
        assert validate_kg_phone("9965551234567") is False
    
    def test_invalid_phone_wrong_prefix(self):
        """Тест невалидного номера - неправильный префикс"""
        assert validate_kg_phone("995555123456") is False
        assert validate_kg_phone("777555123456") is False
    
    def test_invalid_phone_contains_letters(self):
        """Тест невалидного номера - содержит буквы"""
        assert validate_kg_phone("99655512345a") is False
        assert validate_kg_phone("abc996555123456") is False
    
    def test_invalid_phone_empty_string(self):
        """Тест невалидного номера - пустая строка"""
        assert validate_kg_phone("") is False
    
    def test_invalid_phone_only_996(self):
        """Тест невалидного номера - только 996"""
        assert validate_kg_phone("996") is False
    
    def test_valid_phone_edge_cases(self):
        """Тест граничных случаев валидных номеров"""
        assert validate_kg_phone("996000000000") is True
        assert validate_kg_phone("996999999999") is True

    def test_valid_phone_with_spaces_and_plus(self):
        """Тест валидных номеров с пробелами и плюсом"""
        assert validate_kg_phone("+996 888 101 0 01") is True
        assert validate_kg_phone("996 888 101 001") is True
        assert validate_kg_phone("996888101001") is True

