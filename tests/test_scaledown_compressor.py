import pytest
from unittest.mock import patch, MagicMock
from scaledown.compressor.scaledown_compressor import ScaleDownCompressor
from scaledown.exceptions import AuthenticationError, APIError

# Sample data for mocking
MOCK_API_RESPONSE = {
    "results": {
        "compressed_prompt": "Shortened text",
        "original_prompt_tokens": 100,
        "compressed_prompt_tokens": 50
    },
    "latency_ms": 120,
    "model_used": "gpt-4o",
    "request_metadata": {"timestamp": "2025-01-01T12:00:00Z"}
}

@pytest.fixture
def compressor():
    return ScaleDownCompressor(api_key="test-key-123", target_model="gpt-4o")

def test_init_sets_attributes(compressor):
    assert compressor.api_key == "test-key-123"
    assert compressor.target_model == "gpt-4o"
    assert compressor.api_url == "https://api.scaledown.ai/v1/compress"

@patch("requests.post")
def test_compress_single_payload_structure(mock_post, compressor):
    """
    Verifies that the JSON payload is nested correctly under 'scaledown'
    and headers use 'x-api-key'.
    """
    # Setup mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_API_RESPONSE
    mock_post.return_value = mock_response

    # Execute
    compressor.compress(context="Long context", prompt="Question")

    # Assertions
    args, kwargs = mock_post.call_args
    
    # Check URL
    assert args[0] == "https://api.scaledown.ai/v1/compress"
    
    # Check Headers
    assert kwargs["headers"]["x-api-key"] == "test-key-123"
    assert kwargs["headers"]["Content-Type"] == "application/json"
    
    # Check Nested Payload
    payload = kwargs["json"]
    assert payload["context"] == "Long context"
    assert payload["prompt"] == "Question"
    assert payload["model"] == "gpt-4o"
    
    # Verify the 'scaledown' nested dict options
    assert "scaledown" in payload
    assert payload["scaledown"]["rate"] == "auto"
    assert payload["scaledown"]["preserve_keywords"] is False

@patch("requests.post")
@patch("scaledown.types.CompressedPrompt.from_api_response")
def test_response_parsing(mock_from_response, mock_post, compressor):
    """
    Verifies that the raw API response is parsed and passed to CompressedPrompt correctly.
    """
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_API_RESPONSE
    mock_post.return_value = mock_response

    compressor.compress("ctx", "prmt")

    # Check that CompressedPrompt.from_api_response was called with correct content
    mock_from_response.assert_called_once()
    call_args = mock_from_response.call_args
    
    # content arg (first positional or keyword)
    assert call_args.kwargs.get('content') == "Shortened text"
    
    # raw_response arg: Check if tokens were mapped correctly
    raw_metrics = call_args.kwargs.get('raw_response')
    assert raw_metrics["original_prompt_tokens"] == 100
    assert raw_metrics["latency_ms"] == 120

def test_missing_api_key_raises_error():
    # Initialize without key
    comp = ScaleDownCompressor(api_key=None)
    # Ensure base class or global config doesn't provide one accidentally for this test
    comp.api_key = None 
    
    with pytest.raises(AuthenticationError):
        comp.compress("ctx", "prompt")

def test_batch_compression_lists():
    """
    Test that providing lists triggers _compress_batch
    """
    comp = ScaleDownCompressor(api_key="test")
    
    # We mock _compress_single instead of requests to test the threading logic simpler
    with patch.object(comp, '_compress_single') as mock_single:
        mock_single.return_value = "mock_result"
        
        contexts = ["c1", "c2"]
        prompts = ["p1", "p2"]
        
        results = comp.compress(context=contexts, prompt=prompts)
        
        assert len(results) == 2
        assert mock_single.call_count == 2

def test_broadcast_compression():
    """
    Test 1 prompt + N contexts = N requests
    """
    comp = ScaleDownCompressor(api_key="test")
    
    with patch.object(comp, '_compress_single') as mock_single:
        mock_single.return_value = "mock_result"
        
        contexts = ["c1", "c2", "c3"]
        prompt = "single prompt"
        
        results = comp.compress(context=contexts, prompt=prompt)
        
        assert len(results) == 3
        # Ensure the single prompt was used for all calls
        call_args = mock_single.call_args_list
        assert call_args[0][0][1] == "single prompt"
        assert call_args[1][0][1] == "single prompt"
