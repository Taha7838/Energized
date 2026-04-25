# backend/tools/search_tool.py

import logging
from tavily import TavilyClient
from crewai.tools import BaseTool
from pydantic import Field
from core.settings import settings

logger = logging.getLogger(__name__)


def _init_tavily() -> TavilyClient:
    """Initialize Tavily client. Fails loudly if API key is invalid."""
    try:
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        logger.info("[Tavily] Client initialized successfully.")
        return client
    except Exception as e:
        raise RuntimeError(f"[Tavily] Failed to initialize client: {e}")


try:
    _tavily_client = _init_tavily()
except RuntimeError as e:
    import sys
    print(f"\n{e}\n")
    sys.exit(1)


class EnergySearchTool(BaseTool):
    name: str = "Energy Industry Web Search"
    description: str = (
        "Searches the web for up-to-date information specifically related to "
        "the energy industry. Use this tool to find recent news, research, "
        "statistics, trends, and developments in areas such as renewable energy, "
        "oil and gas, nuclear power, energy policy, grid infrastructure, and "
        "energy markets. Input should be a specific search query string."
    )
    max_results: int = Field(default=5)

    def _run(self, query: str) -> str:
        """
        Execute a web search using Tavily and return formatted results.
        Fails gracefully — returns error string instead of crashing the agent.
        """
        logger.info(f"[Tavily] Searching for: '{query}'")

        try:
            response = _tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=self.max_results,
                include_answer=True,
                include_raw_content=False,
            )
        except Exception as e:
            logger.error(f"[Tavily] Search failed for '{query}': {e}")
            return f"Search failed: {e}. Try rephrasing the query."

        if not response or "results" not in response:
            logger.warning(f"[Tavily] Empty response for query: '{query}'")
            return "No results found. Try a different search query."

        output_parts = []

        # Include Tavily's own AI answer if available
        if response.get("answer"):
            output_parts.append(f"SUMMARY ANSWER:\n{response['answer']}\n")

        output_parts.append("SEARCH RESULTS:")

        for i, result in enumerate(response["results"], 1):
            title = result.get("title", "No title")
            url = result.get("url", "No URL")
            content = result.get("content", "No content available")
            score = result.get("score", 0)

            output_parts.append(
                f"\n[{i}] {title}\n"
                f"    URL: {url}\n"
                f"    Relevance: {score:.2f}\n"
                f"    Content: {content[:500]}{'...' if len(content) > 500 else ''}"
            )

        formatted = "\n".join(output_parts)
        logger.info(f"[Tavily] Returned {len(response['results'])} results.")
        return formatted