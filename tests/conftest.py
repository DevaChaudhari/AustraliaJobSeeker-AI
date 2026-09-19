import pytest


@pytest.fixture(autouse=True)
def _no_real_llm_key(monkeypatch):
    """Keep tests offline: never pick up a real key from the developer's environment."""
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
