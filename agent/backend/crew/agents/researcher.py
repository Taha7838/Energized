# backend/crew/agents/researcher.py

import logging
from crewai import Agent, LLM
from tools.search_tool import EnergySearchTool
from core.settings import settings

logger = logging.getLogger(__name__)


def _init_llm() -> LLM:
    """Initialize Gemini LLM via CrewAI's LiteLLM wrapper."""
    try:
        llm = LLM(
            model=f"gemini/{settings.GEMINI_MODEL}",
            api_key=settings.GEMINI_API_KEY,
            temperature=0.3,
        )
        logger.info(f"[Researcher] LLM initialized: {settings.GEMINI_MODEL}")
        return llm
    except Exception as e:
        raise RuntimeError(
            f"[Researcher] Failed to initialize Gemini LLM: {e}"
        )


_llm: LLM | None = None


def _get_llm() -> LLM:
    global _llm
    if _llm is None:
        _llm = _init_llm()
    return _llm


def build_researcher_agent() -> Agent:
    """
    Builds and returns the Researcher Agent.
    Responsible for searching the web and collecting raw findings.
    """
    try:
        search_tool = EnergySearchTool()

        agent = Agent(
            role="Senior Energy Industry Research Analyst",
            goal=(
                "Conduct thorough and accurate web research on energy industry topics. "
                "Search for the most recent, relevant, and credible information from "
                "multiple sources. Focus on facts, statistics, expert opinions, and "
                "recent developments in the energy sector."
            ),
            backstory=(
                "You are a seasoned research analyst with over 15 years of experience "
                "in the global energy industry. You have deep expertise in renewable "
                "energy, fossil fuels, energy policy, grid infrastructure, and energy "
                "markets. You are known for finding accurate, up-to-date information "
                "from credible sources and presenting raw findings in a clear, "
                "organized manner for further analysis."
            ),
            tools=[search_tool],
            llm=_get_llm(),
            verbose=True,
            allow_delegation=False,
            max_iter=5,
        )

        logger.info("[Researcher] Agent built successfully.")
        return agent

    except Exception as e:
        raise RuntimeError(f"[Researcher] Failed to build agent: {e}")