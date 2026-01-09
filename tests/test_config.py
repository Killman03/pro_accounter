import pytest
from unittest.mock import patch
import os
from config import BOT_TOKEN, ADMIN_ID, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME


class TestConfig:
    """Тесты для конфигурации"""
    
    def test_bot_token_default(self):
        """Тест значения по умолчанию для BOT_TOKEN"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('config.load_dotenv'):
                # Перезагружаем модуль для применения изменений
                import importlib
                import config
                importlib.reload(config)
                # Проверяем что есть значение по умолчанию
                assert config.BOT_TOKEN is not None
    
    def test_admin_id_default(self):
        """Тест значения по умолчанию для ADMIN_ID"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('config.load_dotenv'):
                import importlib
                import config
                importlib.reload(config)
                # Проверяем что есть значение по умолчанию
                assert isinstance(config.ADMIN_ID, int)
    
    def test_db_config_defaults(self):
        """Тест значений по умолчанию для настроек БД"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('config.load_dotenv'):
                import importlib
                import config
                importlib.reload(config)
                # Проверяем что есть значения по умолчанию
                assert config.DB_HOST is not None
                assert isinstance(config.DB_PORT, int)
                assert config.DB_USER is not None
                assert config.DB_PASSWORD is not None
                assert config.DB_NAME is not None
    
    def test_config_values_exist(self):
        """Тест что все конфигурационные значения существуют"""
        assert BOT_TOKEN is not None
        assert isinstance(ADMIN_ID, int)
        assert DB_HOST is not None
        assert isinstance(DB_PORT, int)
        assert DB_USER is not None
        assert DB_PASSWORD is not None
        assert DB_NAME is not None



