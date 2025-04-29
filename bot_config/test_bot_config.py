import pytest
import os
from unittest.mock import patch
from bot_config.bot_config import load_config

def test_load_config_success():
    with patch.dict(os.environ, {
        'GOOGLE_ICAL_URL': 'http://example.com/calendar',
        'DISCORD_BOT_TOKEN': 'fake_token',
        'DISCORD_GUILD_ID': '1234567890'
    }):
        config = load_config()
        assert config["ICAL_URL"] == "http://example.com/calendar"
        assert config["DISCORD_BOT_TOKEN"] == "fake_token"
        assert config["DISCORD_GUILD_ID"] == 1234567890

def test_load_config_missing_variable():
    with patch('os.getenv') as mock_getenv:
        mock_getenv.side_effect = lambda key: {
            'GOOGLE_ICAL_URL': 'http://example.com/calendar',
            'DISCORD_BOT_TOKEN': 'fake_token'
            # Missing DISCORD_GUILD_ID
        }.get(key, None)
        
        with pytest.raises(KeyError):
            load_config()

def test_load_config_invalid_guild_id():
    with patch.dict(os.environ, {
        'GOOGLE_ICAL_URL': 'http://example.com/calendar',
        'DISCORD_BOT_TOKEN': 'fake_token',
        'DISCORD_GUILD_ID': 'invalid_id'
    }):
        with pytest.raises(ValueError):
            load_config()

def test_load_config_with_spaces():
    with patch.dict(os.environ, {
        'GOOGLE_ICAL_URL': '  http://example.com/calendar  ',
        'DISCORD_BOT_TOKEN': 'fake_token  ',
        'DISCORD_GUILD_ID': ' 1234567890 '
    }):
        config = load_config()
        assert config["ICAL_URL"] == "http://example.com/calendar"
        assert config["DISCORD_BOT_TOKEN"] == "fake_token"
        assert config["DISCORD_GUILD_ID"] == 1234567890

def test_load_config_missing_env_file_with_env_vars():
    with patch.dict(os.environ, {
        'GOOGLE_ICAL_URL': 'http://example.com/calendar',
        'DISCORD_BOT_TOKEN': 'fake_token',
        'DISCORD_GUILD_ID': '1234567890'
    }):
        config = load_config()
        assert config["ICAL_URL"] == "http://example.com/calendar"
        assert config["DISCORD_BOT_TOKEN"] == "fake_token"
        assert config["DISCORD_GUILD_ID"] == 1234567890

def test_load_config_with_empty_values():
    with patch.dict(os.environ, {
        'GOOGLE_ICAL_URL': '',
        'DISCORD_BOT_TOKEN': 'fake_token',
        'DISCORD_GUILD_ID': '1234567890'
    }):
        with pytest.raises(KeyError):
            load_config()

def test_load_config_called_once():
    with patch.dict(os.environ, {
        'GOOGLE_ICAL_URL': 'http://example.com/calendar',
        'DISCORD_BOT_TOKEN': 'fake_token',
        'DISCORD_GUILD_ID': '1234567890'
    }) as mock_env:
        load_config()
        load_config()
        assert mock_env['GOOGLE_ICAL_URL'] == 'http://example.com/calendar'

def test_load_config_with_valid_env():
    with patch.dict(os.environ, {
        'GOOGLE_ICAL_URL': 'http://example.com/calendar',
        'DISCORD_BOT_TOKEN': 'fake_token',
        'DISCORD_GUILD_ID': '1234567890'
    }):
        config = load_config()
        assert config["ICAL_URL"] == "http://example.com/calendar"
        assert config["DISCORD_BOT_TOKEN"] == "fake_token"
        assert config["DISCORD_GUILD_ID"] == 1234567890
