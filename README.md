```markdown
# scaledown

The official Python client for the ScaleDown API. This package allows you to compress long contexts and prompts to reduce token usage and latency while maintaining model performance on downstream tasks.

## Features

- **Context Compression**: Reduce token count for RAG, long-document QA, and chat history.
- **Model-Aware**: Optimizes compression for specific target models (e.g., `gpt-4o`).
- **Batch Processing**: Built-in threaded execution for compressing multiple inputs in parallel.
- **Easy Integration**: Drop-in replacement compatible with standard prompt engineering workflows.

## Installation

```
pip install scaledown
```

## Configuration

You can configure the client using environment variables or by passing arguments directly.

### Environment Variables

Set your API key globally to avoid passing it in every request:

```
export SCALEDOWN_API_KEY="sk-..."
```

Optionally, you can override the default API endpoint (useful for enterprise or staging environments):

```
export SCALEDOWN_API_URL="https://api.scaledown.ai/v1/compress"
```

## Usage

### Basic Compression

Initialize the compressor and pass your context and prompt.

```
from scaledown.compressor.scaledown_compressor import ScaleDownCompressor

# Initialize with your API key
compressor = ScaleDownCompressor(
    api_key="your-api-key",
    target_model="gpt-4o",
    rate="auto"
)

context = """
[Long text about quantum physics history...]
"""
prompt = "Who were the key figures mentioned?"

# Compress
compressed_result = compressor.compress(context=context, prompt=prompt)

# Access results
print("Compressed Text:\n", compressed_result.content)
print("\nMetrics:", compressed_result.metrics)
# Output: {'original_prompt_tokens': 1500, 'compressed_prompt_tokens': 450, ...}
```

### Batch Processing

To improve throughput, you can pass lists of contexts and prompts. The client automatically uses threading (default 5 workers) to process them in parallel.

```
contexts = ["Context A...", "Context B...", "Context C..."]
prompts = ["Question A", "Question B", "Question C"]

# Returns a list of CompressedPrompt objects
results = compressor.compress(context=contexts, prompt=prompts)

for res in results:
    print(f"Reduced tokens from {res.metrics['original_prompt_tokens']} to {res.metrics['compressed_prompt_tokens']}")
```

### Broadcasting Prompts

If you have multiple contexts (e.g., different documents) but one single prompt (e.g., "Summarize this"), you can pass the prompt as a string and the context as a list.

```
docs = ["Doc 1 content...", "Doc 2 content..."]
query = "Extract key dates."

results = compressor.compress(context=docs, prompt=query)
```

## Advanced Options

You can fine-tune the compression behavior using the constructor or the `compress` method:

- **`preserve_keywords`**: Ensure specific entities or terms are kept.
- **`preserve_words`**: A list of specific words to force-keep in the output.
- **`temperature`**: Control the stochasticity of the compression model.

```
compressor = ScaleDownCompressor(
    api_key="...",
    preserve_keywords=True,
    preserve_words=["critical_variable_x"],
    temperature=0.2
)
```

## Development & Testing

To contribute to this package:

1. **Clone the repository:**
   ```
   git clone https://github.com/ilatims-b/scaledown.git
   cd scaledown
   ```

2. **Install in editable mode:**
   ```
   pip install -e .
   ```

3. **Run Tests:**
   The repository includes a `tests/` directory. Use `pytest` to run them:
   ```
   pip install pytest requests
   pytest tests/
   ```

## License

[MIT License](LICENSE)
```
