# backend/crew/tasks/research_task.py
import logging
from crewai import Task, Agent

logger = logging.getLogger(__name__)


def build_research_task(agent: Agent, query: str) -> Task:
    try:
        task = Task(
            description=(
                f"Research the following energy industry topic thoroughly:\n\n"
                f"QUERY: {query}\n\n"
                f"Your job is to search the web using the available search tool and "
                f"gather comprehensive, up-to-date information. You MUST:\n"
                f"1. Perform at least 2-3 distinct searches to get broad coverage\n"
                f"2. Collect key facts, statistics, recent developments, and expert opinions\n"
                f"3. Note the URL source for every piece of information you find\n"
                f"4. Focus only on credible sources (news agencies, government reports, "
                f"industry publications, academic sources)\n"
                f"5. Cover multiple angles: market trends, technology, policy, economics\n\n"
                f"Present your findings as structured raw notes — do NOT summarize or "
                f"editorialize. The analyst will handle synthesis. Your job is thorough "
                f"data collection."
            ),
            expected_output=(
                "A structured collection of raw research findings containing:\n"
                "- Key facts and statistics from multiple searches\n"
                "- Recent developments and news (with dates when available)\n"
                "- Expert quotes or opinions (attributed)\n"
                "- A list of all source URLs consulted\n"
                "- Any conflicting data points or uncertainties noted explicitly\n"
                "Format: clearly labeled sections, bullet points for facts, "
                "source URLs listed at the end of each section."
            ),
            agent=agent,
        )
        logger.info(f"[ResearchTask] Task built for query: '{query}'")
        return task
    except Exception as e:
        raise RuntimeError(f"[ResearchTask] Failed to build task: {e}")