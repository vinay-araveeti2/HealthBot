from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Literal
import os
import json
import re
from dotenv import load_dotenv
import cohere
from types import SimpleNamespace

from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END

from prompts import SUMMARY_PROMPT, QUIZ_PROMPT, GRADE_PROMPT


@dataclass
class HealthBotState:
    topic: Optional[str] = None
    tavily_results: Optional[List[Dict[str, Any]]] = None
    sources: Optional[str] = None
    summary: Optional[str] = None
    quiz_question: Optional[str] = None
    quiz_expected_answer: Optional[str] = None
    patient_answer: Optional[str] = None
    grade: Optional[str] = None
    grade_explanation: Optional[str] = None
    grade_citations: Optional[List[str]] = None
    next_action: Optional[Literal["restart", "exit"]] = None


# ----------------------------
# ENV
# ----------------------------
def init_env():
    config_path = os.path.join(os.path.dirname(__file__), "config.env")
    load_dotenv(config_path)
    assert os.getenv("COHERE_API_KEY"), "Missing COHERE_API_KEY in config.env"
    assert os.getenv("TAVILY_API_KEY"), "Missing TAVILY_API_KEY in config.env"


# ----------------------------
# LLM (Cohere Adapter)
# ----------------------------
def build_llm():
    api_key = os.getenv("COHERE_API_KEY")
    client = cohere.Client(api_key)

    class CohereAdapter:
        def __init__(self, client, model: str = "command-r7b-12-2024"):
            self.client = client
            self.model = "command-r7b-12-2024"  # Currently available model (Dec 2024)
            self.max_tokens = 650
            self.temperature = 0.2

        def invoke(self, prompt: str):
            resp = self.client.chat(
                model=self.model,
                message=prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            text = ""
            if resp and getattr(resp, "text", None):
                text = resp.text
            return SimpleNamespace(content=text)

    return CohereAdapter(client)


# ----------------------------
# Tavily
# ----------------------------
def build_tavily():
    return TavilySearchResults(k=5)


def _format_sources(results: List[Dict[str, Any]]) -> str:
    lines = []
    for i, r in enumerate(results, start=1):
        title = r.get("title", "Untitled")
        url = r.get("url", "")
        lines.append(f"SRC{i}: {title} — {url}")
    return "\n".join(lines)


def _concat_results_text(results: List[Dict[str, Any]], max_chars: int = 12000) -> str:
    out, total = [], 0
    for r in results:
        content = (r.get("content") or "").strip()
        if not content:
            continue
        if total + len(content) > max_chars:
            break
        out.append(content)
        total += len(content)
    return "\n\n".join(out)


# ----------------------------
# Robust JSON extraction (fixes json.loads failures)
# ----------------------------
def _safe_json_loads(text: str) -> Dict[str, Any]:
    """
    Cohere may return extra text around JSON.
    This extracts the first {...} block and parses it.
    """
    if not text:
        raise ValueError("Empty model output; expected JSON.")

    # Try direct parse first
    try:
        return json.loads(text)
    except Exception:
        pass

    # Extract first JSON object block
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Model did not return JSON. Output was:\n{text}")

    return json.loads(match.group(0))


# ----------------------------
# Nodes
# ----------------------------
def node_search(state: HealthBotState) -> HealthBotState:
    tavily = build_tavily()
    query = f"{state.topic} site:cdc.gov OR site:who.int OR site:nih.gov OR site:mayoclinic.org OR site:nhs.uk"
    res = tavily.invoke({"query": query})
    results = res.get("results") if isinstance(res, dict) else res

    state.tavily_results = results or []
    state.sources = _format_sources(state.tavily_results)
    return state


def node_summarize(state: HealthBotState) -> HealthBotState:
    llm = build_llm()
    results_text = _concat_results_text(state.tavily_results or [])
    prompt = SUMMARY_PROMPT.format(sources=state.sources or "", results_text=results_text)
    resp = llm.invoke(prompt)
    state.summary = (resp.content or "").strip()
    return state


def node_make_quiz(state: HealthBotState) -> HealthBotState:
    llm = build_llm()
    prompt = QUIZ_PROMPT.format(summary=state.summary or "")
    resp = llm.invoke(prompt)
    data = _safe_json_loads(resp.content)

    state.quiz_question = data.get("question")
    state.quiz_expected_answer = data.get("expected_answer")
    return state


def node_grade_answer(state: HealthBotState) -> HealthBotState:
    llm = build_llm()
    prompt = GRADE_PROMPT.format(
        summary=state.summary or "",
        question=state.quiz_question or "",
        patient_answer=state.patient_answer or "",
    )
    resp = llm.invoke(prompt)
    data = _safe_json_loads(resp.content)

    state.grade = data.get("grade")
    state.grade_explanation = data.get("explanation")
    state.grade_citations = data.get("citations", [])
    return state


def node_reset(state: HealthBotState) -> HealthBotState:
    state.topic = None
    state.tavily_results = None
    state.sources = None
    state.summary = None
    state.quiz_question = None
    state.quiz_expected_answer = None
    state.patient_answer = None
    state.grade = None
    state.grade_explanation = None
    state.grade_citations = None
    state.next_action = None
    return state


# ----------------------------
# Build separate graphs (fixes "node call" issues)
# ----------------------------
def build_graphs():
    """
    Returns 3 compiled graphs:
      - learn_graph: search -> summarize -> make_quiz -> END
      - grade_graph: grade_answer -> END
      - reset_graph: reset -> END
    """
    # Learn graph
    g1 = StateGraph(HealthBotState)
    g1.add_node("search", node_search)
    g1.add_node("summarize", node_summarize)
    g1.add_node("make_quiz", node_make_quiz)
    g1.set_entry_point("search")
    g1.add_edge("search", "summarize")
    g1.add_edge("summarize", "make_quiz")
    g1.add_edge("make_quiz", END)
    learn_graph = g1.compile()

    # Grade graph
    g2 = StateGraph(HealthBotState)
    g2.add_node("grade_answer", node_grade_answer)
    g2.set_entry_point("grade_answer")
    g2.add_edge("grade_answer", END)
    grade_graph = g2.compile()

    # Reset graph
    g3 = StateGraph(HealthBotState)
    g3.add_node("reset", node_reset)
    g3.set_entry_point("reset")
    g3.add_edge("reset", END)
    reset_graph = g3.compile()

    return learn_graph, grade_graph, reset_graph


def build_graph():
    """Wrapper for compatibility: returns the learn_graph."""
    learn_graph, _, _ = build_graphs()
    return learn_graph