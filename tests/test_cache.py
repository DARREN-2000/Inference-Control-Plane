import hashlib

from inference_control_plane.services.cache import _cache_key

def test_cache_key_generation():
    prompt = "Hello"
    model = "gpt-4"
    expected = "cache:inference:" + hashlib.sha256(b"gpt-4:Hello").hexdigest()
    assert _cache_key(prompt, model) == expected
