---
name: anthropic-api
description: Expert knowledge in integrating with the Anthropic Claude API, including prompt engineering, API client configuration, response parsing, error handling, rate limiting, caching, retry logic, and structured output extraction. Use this skill when implementing Claude API calls, designing prompts for analysis tasks, handling API errors, managing API quotas, or parsing LLM responses into structured data.
allowed-tools: [Read, Write, Bash]
---

# Anthropic Claude API Integration Skill

Comprehensive knowledge for building robust applications with the Anthropic Claude API, specialized for structured data extraction and project analysis.

## API Client Setup

### Basic Configuration

```python
from anthropic import Anthropic, AsyncAnthropic
import os

# Sync client
client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

# Async client
async_client = AsyncAnthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)
```

### Environment Variables

```bash
# Required
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional
export ANTHROPIC_BASE_URL="https://api.anthropic.com"  # Custom endpoint
export ANTHROPIC_TIMEOUT=600  # Request timeout in seconds
```

### Client Configuration

```python
class ClaudeClient:
    """Configured Claude API client."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-sonnet-4",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        timeout: float = 600.0
    ):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY required")

        self.client = Anthropic(
            api_key=self.api_key,
            timeout=timeout
        )

        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
```

## Message Creation

### Basic Message

```python
response = client.messages.create(
    model="claude-sonnet-4",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude!"}
    ]
)

# Extract text
text = response.content[0].text
print(text)
```

### With System Prompt

```python
response = client.messages.create(
    model="claude-sonnet-4",
    max_tokens=1024,
    system="You are a helpful assistant specializing in Python programming.",
    messages=[
        {"role": "user", "content": "How do I read a file in Python?"}
    ]
)
```

### Multi-Turn Conversation

```python
messages = []

# User message
messages.append({
    "role": "user",
    "content": "What is FastAPI?"
})

# Get response
response = client.messages.create(
    model="claude-sonnet-4",
    max_tokens=1024,
    messages=messages
)

# Add assistant response
messages.append({
    "role": "assistant",
    "content": response.content[0].text
})

# Continue conversation
messages.append({
    "role": "user",
    "content": "How do I create a route?"
})

response = client.messages.create(
    model="claude-sonnet-4",
    max_tokens=1024,
    messages=messages
)
```

## Prompt Engineering for Structured Output

### JSON Output Prompts

```python
ANALYSIS_SYSTEM_PROMPT = """You are a project analyzer. Extract structured information from project descriptions.

IMPORTANT: Respond ONLY with valid JSON. No markdown, no explanations.

Required JSON structure:
{
  "project_name": "string",
  "project_type": "saas | api | mobile | hardware",
  "tech_stack": {
    "backend": "string",
    "frontend": "string | null",
    "database": "string"
  },
  "features": ["string"],
  "estimated_complexity": "low | medium | high"
}

Guidelines:
- Infer project type from description
- Choose appropriate tech stack
- List only explicitly mentioned features
- Be conservative with complexity estimate
"""

def analyze_project(description: str) -> dict:
    """Analyze project description and return structured data."""

    user_prompt = f"""Analyze this project description:

{description}

Respond with JSON only."""

    response = client.messages.create(
        model="claude-sonnet-4",
        max_tokens=2000,
        temperature=0.3,  # Lower for consistency
        system=ANALYSIS_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}]
    )

    # Parse JSON from response
    import json
    return json.loads(response.content[0].text)
```

### Few-Shot Examples

```python
SYSTEM_PROMPT_WITH_EXAMPLES = """You are a project type classifier.

Examples:

Input: "Build a REST API for user management with FastAPI"
Output: {"type": "api-service", "framework": "python-fastapi"}

Input: "Create a mobile app for tracking expenses"
Output: {"type": "mobile-app", "framework": "react-native"}

Input: "IoT temperature sensor with Raspberry Pi Pico"
Output: {"type": "hardware-iot", "framework": "micropython"}

Now classify the following project. Respond with JSON only.
"""
```

### Guided Output Format

```python
def create_extraction_prompt(text: str, fields: list[str]) -> str:
    """Create prompt for extracting specific fields."""

    fields_list = '\n'.join(f'- {field}' for field in fields)

    return f"""Extract the following information from the text:

{fields_list}

Text:
{text}

Respond in JSON format with these exact keys: {', '.join(fields)}
"""

# Usage
response = client.messages.create(
    model="claude-sonnet-4",
    max_tokens=1000,
    temperature=0.2,
    messages=[{
        "role": "user",
        "content": create_extraction_prompt(
            "Build a SaaS platform with React and FastAPI",
            ["frontend_framework", "backend_framework", "deployment_type"]
        )
    }]
)
```

## Response Parsing

### Safe JSON Extraction

```python
import json
import re

def extract_json(text: str) -> dict:
    """
    Extract JSON from API response, handling markdown code blocks.

    Args:
        text: Response text that may contain JSON

    Returns:
        Parsed JSON dict

    Raises:
        ValueError: If no valid JSON found
    """
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from code block
    code_block_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    match = re.search(code_block_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding JSON object anywhere
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"No valid JSON found in response:\n{text}")
```

### Validation with Pydantic

```python
from pydantic import BaseModel, Field, ValidationError

class ProjectAnalysis(BaseModel):
    """Validated project analysis response."""
    project_name: str = Field(..., min_length=1)
    project_type: str = Field(..., pattern=r'^(saas|api|mobile|hardware)$')
    tech_stack: dict[str, str]
    features: list[str] = Field(default_factory=list)

def parse_and_validate(response_text: str) -> ProjectAnalysis:
    """Parse JSON and validate with Pydantic."""
    try:
        data = extract_json(response_text)
        return ProjectAnalysis(**data)
    except ValueError as e:
        raise ValueError(f"Invalid JSON: {e}")
    except ValidationError as e:
        raise ValueError(f"Validation failed: {e}")
```

## Error Handling

### Retry Logic

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from anthropic import RateLimitError, APIConnectionError

@retry(
    retry=retry_if_exception_type((RateLimitError, APIConnectionError)),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(3)
)
def call_api_with_retry(prompt: str) -> str:
    """Call API with automatic retry on transient errors."""
    response = client.messages.create(
        model="claude-sonnet-4",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
```

### Comprehensive Error Handling

```python
from anthropic import (
    APIError,
    RateLimitError,
    APIConnectionError,
    AuthenticationError,
    BadRequestError
)

def safe_api_call(prompt: str, system: str = None) -> str:
    """
    Call API with comprehensive error handling.

    Returns:
        Response text

    Raises:
        APIError: On unrecoverable errors
    """
    try:
        response = client.messages.create(
            model="claude-sonnet-4",
            max_tokens=2000,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    except AuthenticationError:
        raise APIError(
            "Invalid API key. Check ANTHROPIC_API_KEY environment variable."
        )

    except RateLimitError as e:
        raise APIError(
            f"Rate limit exceeded: {e}\n"
            "Wait a moment and try again, or upgrade your plan."
        )

    except BadRequestError as e:
        raise APIError(
            f"Invalid request: {e}\n"
            "Check your prompt and parameters."
        )

    except APIConnectionError as e:
        raise APIError(
            f"Connection error: {e}\n"
            "Check your internet connection and try again."
        )

    except APIError as e:
        raise APIError(f"API error: {e}")
```

## Rate Limiting

### Token Bucket Rate Limiter

```python
from datetime import datetime, timedelta
from collections import deque
import time

class RateLimiter:
    """Rate limiter for API calls."""

    def __init__(self, max_calls: int, time_window: int):
        """
        Args:
            max_calls: Maximum calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque()

    def wait_if_needed(self) -> None:
        """Block if rate limit would be exceeded."""
        now = datetime.now()

        # Remove old calls
        cutoff = now - timedelta(seconds=self.time_window)
        while self.calls and self.calls[0] < cutoff:
            self.calls.popleft()

        # Check limit
        if len(self.calls) >= self.max_calls:
            oldest = self.calls[0]
            wait_until = oldest + timedelta(seconds=self.time_window)
            wait_seconds = (wait_until - now).total_seconds()

            if wait_seconds > 0:
                print(f"Rate limit reached. Waiting {wait_seconds:.1f}s...")
                time.sleep(wait_seconds)

        self.calls.append(now)

# Usage
rate_limiter = RateLimiter(max_calls=50, time_window=60)  # 50/min

def rate_limited_call(prompt: str) -> str:
    rate_limiter.wait_if_needed()
    return call_api(prompt)
```

## Caching

### Response Cache

```python
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta

class ResponseCache:
    """Cache API responses to reduce costs."""

    def __init__(self, cache_dir: Path, ttl_days: int = 7):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(days=ttl_days)

    def _get_cache_key(self, prompt: str, system: str = None) -> str:
        """Generate cache key from prompt."""
        content = f"{system or ''}\n{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, prompt: str, system: str = None) -> str | None:
        """Get cached response if available and fresh."""
        key = self._get_cache_key(prompt, system)
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None

        data = json.loads(cache_file.read_text())

        # Check TTL
        cached_at = datetime.fromisoformat(data['cached_at'])
        if datetime.now() - cached_at > self.ttl:
            cache_file.unlink()  # Expired
            return None

        return data['response']

    def set(self, prompt: str, response: str, system: str = None) -> None:
        """Cache a response."""
        key = self._get_cache_key(prompt, system)
        cache_file = self.cache_dir / f"{key}.json"

        data = {
            'prompt': prompt,
            'system': system,
            'response': response,
            'cached_at': datetime.now().isoformat()
        }

        cache_file.write_text(json.dumps(data, indent=2))

# Usage
cache = ResponseCache(Path.home() / '.cache' / 'claude-api')

def call_with_cache(prompt: str, system: str = None) -> str:
    # Check cache first
    cached = cache.get(prompt, system)
    if cached:
        print("Cache hit!")
        return cached

    # Call API
    response = client.messages.create(
        model="claude-sonnet-4",
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.content[0].text

    # Cache response
    cache.set(prompt, text, system)

    return text
```

## Async API Calls

### Basic Async Usage

```python
import asyncio

async def async_analyze(description: str) -> dict:
    """Async project analysis."""
    async_client = AsyncAnthropic(
        api_key=os.getenv('ANTHROPIC_API_KEY')
    )

    response = await async_client.messages.create(
        model="claude-sonnet-4",
        max_tokens=2000,
        system=ANALYSIS_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": description}]
    )

    return extract_json(response.content[0].text)

# Run async function
result = asyncio.run(async_analyze("Build a SaaS app"))
```

### Concurrent API Calls

```python
async def analyze_multiple(descriptions: list[str]) -> list[dict]:
    """Analyze multiple projects concurrently."""
    async_client = AsyncAnthropic(
        api_key=os.getenv('ANTHROPIC_API_KEY')
    )

    async def analyze_one(desc: str) -> dict:
        response = await async_client.messages.create(
            model="claude-sonnet-4",
            max_tokens=2000,
            system=ANALYSIS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": desc}]
        )
        return extract_json(response.content[0].text)

    # Run concurrently
    results = await asyncio.gather(*[
        analyze_one(desc) for desc in descriptions
    ])

    return results

# Usage
descriptions = [
    "Build a REST API",
    "Create a mobile app",
    "IoT sensor device"
]
results = asyncio.run(analyze_multiple(descriptions))
```

## Token Usage Tracking

```python
class TokenTracker:
    """Track API token usage and costs."""

    # Pricing per 1M tokens (update with current pricing)
    PRICES = {
        'claude-sonnet-4': {
            'input': 3.00,   # per 1M input tokens
            'output': 15.00  # per 1M output tokens
        },
        'claude-opus-4': {
            'input': 15.00,
            'output': 75.00
        }
    }

    def __init__(self):
        self.usage = {
            'input_tokens': 0,
            'output_tokens': 0,
            'calls': 0
        }

    def record(self, response):
        """Record usage from API response."""
        self.usage['input_tokens'] += response.usage.input_tokens
        self.usage['output_tokens'] += response.usage.output_tokens
        self.usage['calls'] += 1

    def get_cost(self, model: str = 'claude-sonnet-4') -> float:
        """Calculate total cost."""
        prices = self.PRICES.get(model, self.PRICES['claude-sonnet-4'])

        input_cost = (self.usage['input_tokens'] / 1_000_000) * prices['input']
        output_cost = (self.usage['output_tokens'] / 1_000_000) * prices['output']

        return input_cost + output_cost

    def report(self, model: str = 'claude-sonnet-4') -> str:
        """Generate usage report."""
        cost = self.get_cost(model)
        return f"""API Usage Summary:
  Calls: {self.usage['calls']}
  Input tokens: {self.usage['input_tokens']:,}
  Output tokens: {self.usage['output_tokens']:,}
  Total cost: ${cost:.4f}"""

# Usage
tracker = TokenTracker()

response = client.messages.create(
    model="claude-sonnet-4",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)
tracker.record(response)

print(tracker.report())
```

## Best Practices

1. **Use lower temperature for structured output**
```python
# For consistent JSON output
temperature=0.2  # or 0.3

# For creative text
temperature=0.7  # or higher
```

2. **Validate API key on startup**
```python
def validate_api_key():
    try:
        client.messages.create(
            model="claude-sonnet-4",
            max_tokens=10,
            messages=[{"role": "user", "content": "test"}]
        )
    except AuthenticationError:
        raise ValueError("Invalid ANTHROPIC_API_KEY")
```

3. **Handle timeouts**
```python
from anthropic import APITimeoutError

try:
    response = client.messages.create(
        model="claude-sonnet-4",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        timeout=30.0  # 30 seconds
    )
except APITimeoutError:
    print("Request timed out. Try reducing max_tokens or simplifying prompt.")
```

4. **Use system prompts effectively**
```python
# Good: Clear role and output format
system = "You are a JSON API. Always respond with valid JSON only."

# Bad: Vague instructions
system = "You're helpful"
```

5. **Cache expensive operations**
```python
# Cache project analysis - same input = same output
cached_analysis = cache.get(description)
if not cached_analysis:
    cached_analysis = analyze(description)
    cache.set(description, cached_analysis)
```

## Testing with Mocks

```python
from unittest.mock import Mock, patch

def test_api_call():
    """Test API integration with mock."""
    mock_response = Mock()
    mock_response.content = [Mock(text='{"result": "success"}')]

    with patch.object(client.messages, 'create', return_value=mock_response):
        result = analyze_project("Test project")
        assert result['result'] == 'success'
```

## Quick Reference

**Models:**
- `claude-sonnet-4` - Fast, balanced
- `claude-opus-4` - Most capable, expensive
- `claude-haiku-4` - Fastest, cheapest

**Key Parameters:**
- `model` - Which Claude model
- `max_tokens` - Max response length
- `temperature` - Randomness (0-1)
- `system` - System prompt
- `messages` - Conversation history

**Error Types:**
- `AuthenticationError` - Invalid API key
- `RateLimitError` - Too many requests
- `BadRequestError` - Invalid parameters
- `APIConnectionError` - Network issues
- `APITimeoutError` - Request timeout
