# backend/crew/agents/analyst.py

import logging
from crewai import Agent, LLM
from core.settings import settings

logger = logging.getLogger(__name__)


def _init_llm() -> LLM:
    """Initialize Gemini LLM via CrewAI's LiteLLM wrapper."""
    try:
        llm = LLM(
            model=f"gemini/{settings.GEMINI_MODEL}",
            api_key=settings.GEMINI_API_KEY,
            temperature=0.5,
        )
        logger.info(f"[Analyst] LLM initialized: {settings.GEMINI_MODEL}")
        return llm
    except Exception as e:
        raise RuntimeError(
            f"[Analyst] Failed to initialize Gemini LLM: {e}"
        )


_llm: LLM | None = None


def _get_llm() -> LLM:
    global _llm
    if _llm is None:
        _llm = _init_llm()
    return _llm


def build_analyst_agent() -> Agent:
    """
    Builds and returns the Analyst Agent.
    Responsible for synthesizing raw research into a clean, structured summary.
    """
    try:
        agent = Agent(
            role="Senior Energy Industry Intelligence Analyst",
            goal=(
                "Transform raw research findings into comprehensive, accurate, and "
                "well-structured intelligence reports about the energy industry. "
                "Synthesize information from multiple sources into clear insights "
                "that are actionable and easy to understand."
            ),
            backstory=(
                "You are an elite intelligence analyst specializing in the global "
                "energy sector. You have a talent for taking complex, scattered "
                "research data and distilling it into sharp, coherent narratives. "
                "Your reports are trusted by energy executives, policy makers, and "
                "investors worldwide. You never fabricate information — every claim "
                "in your reports is grounded in the research provided to you. "
                "You always cite your sources and highlight key takeaways clearly."
            ),
            llm=_get_llm(),
            verbose=True,
            allow_delegation=False,
            max_iter=3,
        )

        logger.info("[Analyst] Agent built successfully.")
        return agent

    except Exception as e:
        raise RuntimeError(f"[Analyst] Failed to build agent: {e}")