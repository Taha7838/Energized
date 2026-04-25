# backend/crew/tasks/analysis_task.py
import logging
from crewai import Task, Agent

logger = logging.getLogger(__name__)


def build_analysis_task(agent: Agent, query: str, research_task: Task) -> Task:
    try:
        task = Task(
            description=(
                f"You will receive raw research findings about the following query:\n\n"
                f"QUERY: {query}\n\n"
                f"Your job is to synthesize those findings into a polished intelligence "
                f"report. You MUST:\n"
                f"1. Write a concise executive summary (3-5 sentences) at the top\n"
                f"2. Organize findings into clear thematic sections with headers\n"
                f"3. Highlight the 3-5 most important takeaways in a dedicated section\n"
                f"4. Include all relevant statistics and data points with their sources\n"
                f"5. Note any conflicting information or data gaps explicitly\n"
                f"6. End with a 'Sources' section listing all URLs referenced\n\n"
                f"STRICT RULES:\n"
                f"- Never fabricate information not present in the research findings\n"
                f"- Every claim must trace back to a source from the research\n"
                f"- Write for an audience of energy industry executives and analysts\n"
                f"- Be direct and factual — no filler, no vague generalities"
            ),
            expected_output=(
                "A complete intelligence report with the following structure:\n\n"
                "## Executive Summary\n"
                "[3-5 sentence overview of the most important findings]\n\n"
                "## Key Findings\n"
                "[Thematic sections with headers, facts, and inline source attribution]\n\n"
                "## Critical Takeaways\n"
                "[Bullet list of 3-5 most actionable or significant insights]\n\n"
                "## Data & Statistics\n"
                "[Key numbers, percentages, market figures with sources]\n\n"
                "## Sources\n"
                "[Numbered list of all URLs referenced in the report]\n\n"
                "The report must be comprehensive (400-800 words), well-structured, "
                "and immediately useful to an energy industry professional."
            ),
            agent=agent,
            context=[research_task],
        )
        logger.info(f"[AnalysisTask] Task built for query: '{query}'")
        return task
    except Exception as e:
        raise RuntimeError(f"[AnalysisTask] Failed to build task: {e}")