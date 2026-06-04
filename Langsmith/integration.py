import os
from dotenv import load_dotenv

load_dotenv()


def langsmith_enabled() -> bool:
    """Return True when LangSmith tracing is enabled and an API key is available."""
    enabled = os.getenv("LANGSMITH_TRACING", "false").strip().lower() == "true"
    api_key = os.getenv("LANGSMITH_API_KEY", "").strip()
    return enabled and bool(api_key)


def get_langsmith_tracer_config() -> dict | None:
    """Return the LangSmith tracer config that can be passed to graph.invoke()."""
    if not langsmith_enabled():
        return None

    tracer: dict[str, str] = {}
    tracer["project"] = os.getenv("LANGSMITH_PROJECT") or os.getenv("LANGCHAIN_PROJECT", "")
    example_id = os.getenv("LANGSMITH_EXAMPLE_ID")
    if example_id:
        tracer["example_id"] = example_id

    return tracer


def get_graph_config() -> dict | None:
    """Return the graph invocation config for LangSmith tracing."""
    tracer = get_langsmith_tracer_config()
    if tracer is None:
        return None
    return {"langsmith_tracer": tracer}
