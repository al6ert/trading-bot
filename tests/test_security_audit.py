import pytest
import logging
from app.core.config import Settings
from app.infrastructure.hyperliquid.client import HyperliquidClient

def test_settings_secret_exposure():
    """
    Verify that PRIVATE_KEY is not exposed in string representation or model dump
    when using default settings (which might read from env).
    """
    # Create a settings instance with a dummy key
    # We use monkeypatch to set env var for this test context if needed, 
    # but here we can just instantiate with a value if Pydantic allows, 
    # or rely on the fact that we want to test the class definition.
    
    # Let's try to instantiate Settings with a dummy key via environment variable mock
    import os
    os.environ["PRIVATE_KEY"] = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    
    settings = Settings()
    
    # Check string representation
    assert "0x1234567890abcdef" not in str(settings), "PRIVATE_KEY exposed in str(settings)"
    assert "0x1234567890abcdef" not in repr(settings), "PRIVATE_KEY exposed in repr(settings)"
    
    # Check model dump
    dump = settings.model_dump()
    # Ideally, we want it excluded or masked. 
    # If it's present, it's a fail unless we decide it's acceptable for internal use but not logging.
    # However, for "No-Custodio" strictness, we prefer it hidden.
    
    # If we use SecretStr, it will be hidden in dump unless mode='json' with secrets revealed.
    # Let's assert it is NOT plain text.
    if "PRIVATE_KEY" in dump and dump["PRIVATE_KEY"]:
        val = dump["PRIVATE_KEY"]
        assert str(val) != "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef", "PRIVATE_KEY exposed in model_dump"

def test_client_logging_exposure(caplog):
    """
    Verify HyperliquidClient does not log the private key.
    """
    dummy_key = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    
    with caplog.at_level(logging.DEBUG):
        # Initialize client
        try:
            client = HyperliquidClient(private_key=dummy_key)
        except Exception:
            # It might fail to connect or create account if key is invalid format, 
            # but we just want to check logs produced during init.
            pass
            
    # Check logs
    for record in caplog.records:
        assert dummy_key not in record.message, f"Private key found in log: {record.message}"
