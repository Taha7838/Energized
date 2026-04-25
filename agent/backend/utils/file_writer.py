# backend/utils/file_writer.py

import logging
from datetime import datetime
from pathlib import Path

from core.settings import settings

logger = logging.getLogger(__name__)


def append_to_knowledge_base(
    query: str,
    summary: str,
    sources: list[str],
    from_cache: bool = False,
) -> None:
    """
    Appends a research result to the knowledge base text file.
    Creates the file if it doesn't exist.
    Fails loudly if the file cannot be written.
    """
    path = Path(settings.KNOWLEDGE_BASE_PATH)

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"[FileWriter] Cannot create output directory: {e}")
        raise

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    source_label = "CACHE" if from_cache else "LIVE"

    entry = (
        f"{'='*70}\n"
        f"DATE     : {timestamp}\n"
        f"SOURCE   : {source_label}\n"
        f"QUERY    : {query}\n"
        f"{'='*70}\n\n"
        f"{summary}\n\n"
        f"SOURCES:\n"
    )

    for i, source in enumerate(sources, 1):
        entry += f"  [{i}] {source}\n"

    entry += "\n"

    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(entry)
        logger.info(f"[FileWriter] Appended result to: {path}")
    except Exception as e:
        logger.error(f"[FileWriter] Failed to write to knowledge base: {e}")
        raise