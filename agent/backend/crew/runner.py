# backend/crew/runner.py
import logging
import queue
import re
from datetime import datetime
from typing import Callable

from crewai import Crew, Process

from crew.agents.researcher import build_researcher_agent
from crew.agents.analyst import build_analyst_agent
from crew.tasks.research_task import build_research_task
from crew.tasks.analysis_task import build_analysis_task
from memory.vector_store import store_result
from utils.file_writer import append_to_knowledge_base

logger = logging.getLogger(__name__)

# Regex to strip ANSI escape codes that CrewAI injects into verbose output
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _clean(text: str) -> str:
    return _ANSI_RE.sub("", text).strip()


def _extract_sources(report_text: str) -> list[str]:
    """
    Parse the '## Sources' section from the analyst's report.
    Falls back to extracting bare URLs from the full text if section is absent.
    """
    sources: list[str] = []

    # Try to find the Sources section first
    sources_match = re.search(
        r"##\s*Sources\s*\n(.*?)(?=\n##|\Z)", report_text, re.DOTALL | re.IGNORECASE
    )
    if sources_match:
        block = sources_match.group(1)
        # Match lines like "[1] https://..." or "- https://..." or bare URLs
        urls = re.findall(
            r"https?://[^\s\)\]\,\"\']+", block
        )
        sources = [u.rstrip(".,;)") for u in urls]

    # Fallback: scan entire text for URLs if section parsing found nothing
    if not sources:
        urls = re.findall(r"https?://[^\s\)\]\,\"\']+", report_text)
        sources = list(dict.fromkeys(u.rstrip(".,;)") for u in urls))  # deduplicated

    return sources[:10]  # cap at 10 sources


def run_research_crew(
    query: str,
    stream_queue: queue.Queue | None = None,
) -> dict:
    """
    Builds and runs the CrewAI crew for the given query.

    Args:
        query: The research question.
        stream_queue: If provided, intermediate agent output is pushed here
                      as string messages for SSE streaming.

    Returns:
        dict with keys: query, summary, sources, timestamp, from_cache
    """

    def _emit(msg: str) -> None:
        """Push a message to the SSE queue if one exists."""
        if stream_queue is not None:
            cleaned = _clean(msg)
            if cleaned:
                stream_queue.put(cleaned)

    def _step_callback(step_output) -> None:
        """
        CrewAI calls this after every agent reasoning step.
        step_output is an AgentFinish or AgentAction-like object.
        We defensively stringify whatever we get.
        """
        try:
            if hasattr(step_output, "log"):
                _emit(step_output.log)
            elif hasattr(step_output, "text"):
                _emit(step_output.text)
            elif hasattr(step_output, "return_values"):
                output = step_output.return_values.get("output", "")
                _emit(str(output))
            else:
                _emit(str(step_output))
        except Exception as cb_err:
            logger.warning(f"[Runner] step_callback extraction failed: {cb_err}")

    logger.info(f"[Runner] Starting crew for query: '{query}'")
    _emit(f"🔍 Starting research for: {query}")

    try:
        # Build agents fresh per run — avoids state bleed between requests
        researcher = build_researcher_agent()
        analyst = build_analyst_agent()

        research_task = build_research_task(agent=researcher, query=query)
        analysis_task = build_analysis_task(
            agent=analyst, query=query, research_task=research_task
        )

        crew = Crew(
            agents=[researcher, analyst],
            tasks=[research_task, analysis_task],
            process=Process.sequential,
            verbose=True,
            step_callback=_step_callback,
        )

        _emit("🤖 Researcher agent is gathering information from the web...")
        result = crew.kickoff()

        # CrewAI 0.80.x returns a CrewOutput object; get the string report
        if hasattr(result, "raw"):
            report_text = result.raw
        elif hasattr(result, "final_output"):
            report_text = result.final_output
        else:
            report_text = str(result)

        report_text = _clean(report_text)
        _emit("✅ Analysis complete. Saving results...")

        sources = _extract_sources(report_text)
        timestamp = datetime.utcnow().isoformat()

        # Persist to vector store and flat file
        try:
            store_result(query=query, summary=report_text, sources=sources)
        except Exception as e:
            logger.error(f"[Runner] Failed to store result in ChromaDB: {e}")

        try:
            append_to_knowledge_base(
                query=query,
                summary=report_text,
                sources=sources,
                from_cache=False,
            )
        except Exception as e:
            logger.error(f"[Runner] Failed to append to knowledge base: {e}")

        _emit("💾 Results saved to knowledge base.")

        return {
            "query": query,
            "summary": report_text,
            "sources": sources,
            "timestamp": timestamp,
            "from_cache": False,
        }

    except Exception as e:
        error_msg = f"[Runner] Crew execution failed for query '{query}': {e}"
        logger.error(error_msg)
        _emit(f"❌ Research failed: {e}")
        raise RuntimeError(error_msg) from e