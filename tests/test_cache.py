import pytest
import hashlib
from app.services.cache import _cache_key

def test_cache_key_generation():
    prompt = "Hello"
    model = "gpt-4"
    expected = "cache:inference:" + hashlib.sha256(b"gpt-4:Hello").hexdigest()
    assert _cache_key(prompt, model) == expected
