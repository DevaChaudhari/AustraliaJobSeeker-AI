import pytest

from australiajobseeker.agents import cover_letter_agent, resume_agent


class FakeResponse:
    def __init__(self, content):
        self.content = content


class FakeLLM:
    def __init__(self, contents):
        self.contents = list(contents)
        self.calls = 0

    def invoke(self, prompt):
        self.calls += 1
        return FakeResponse(self.contents.pop(0))


def _resume(monkeypatch, llm):
    monkeypatch.setattr(resume_agent, "_get_llm", lambda temperature=0: llm)
    return resume_agent.tailor_resume("my resume", "a job")


def _cover(monkeypatch, llm):
    monkeypatch.setattr(cover_letter_agent, "_get_llm", lambda temperature=0.3: llm)
    return cover_letter_agent.generate_cover_letter("my resume", "a job", "Acme", "Dev")


@pytest.mark.parametrize("run", [_resume, _cover])
def test_empty_response_is_retried(monkeypatch, run):
    llm = FakeLLM(["", "   ", "real text"])
    assert run(monkeypatch, llm) == "real text"
    assert llm.calls == 3


@pytest.mark.parametrize("run", [_resume, _cover])
def test_repeated_empty_response_raises(monkeypatch, run):
    llm = FakeLLM(["", "", ""])
    with pytest.raises(RuntimeError, match="empty response"):
        run(monkeypatch, llm)
    assert llm.calls == 3
