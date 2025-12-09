import os
import pytest
from scaledown.compressor import config

def test_default_api_url():
    # Ensure env var is not set
    if "SCALEDOWN_API_URL" in os.environ:
        del os.environ["SCALEDOWN_API_URL"]
        
    assert config.get_api_url() == "https://api.scaledown.ai/v1/compress"

def test_custom_api_url_from_env():
    custom_url = "https://staging.scaledown.ai/v1/compress"
    os.environ["SCALEDOWN_API_URL"] = custom_url
    
    try:
        assert config.get_api_url() == custom_url
    finally:
        del os.environ["SCALEDOWN_API_URL"]
