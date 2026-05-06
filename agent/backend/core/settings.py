# backend/core/settings.py

from pydantic_settings import BaseSettings
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent

# Explicitly resolve .env path and verify it exists at import time
ENV_FILE = BASE_DIR / ".env"

if not ENV_FILE.exists():
    print(f"\n[STARTUP ERROR] .env file not found at: {ENV_FILE}")
    print("Create it with GEMINI_API_KEY and TAVILY_API_KEY set.\n")
    sys.exit(1)


class Settings(BaseSettings):
    # API Keys
    GEMINI_API_KEY: str
    TAVILY_API_KEY: str

    # Gemini model
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"

    # ChromaDB
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "memory" / "chroma_store")
    CHROMA_COLLECTION_NAME: str = "energy_research"
    SIMILARITY_THRESHOLD: float = 0.80

    # Output
    KNOWLEDGE_BASE_PATH: str = str(BASE_DIR / "output" / "knowledge_base.txt")

    # CORS
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = str(ENV_FILE)
        extra = "ignore"


def _validate_settings(s: Settings) -> None:
    errors = []

    if not s.GEMINI_API_KEY or s.GEMINI_API_KEY == "your_gemini_api_key_here":
        errors.append("  - GEMINI_API_KEY is missing or not set in .env")

    if not s.TAVILY_API_KEY or s.TAVILY_API_KEY == "your_tavily_api_key_here":
        errors.append("  - TAVILY_API_KEY is missing or not set in .env")

    if not (0.0 < s.SIMILARITY_THRESHOLD <= 1.0):
        errors.append(
            f"  - SIMILARITY_THRESHOLD must be between 0 and 1, "
            f"got {s.SIMILARITY_THRESHOLD}"
        )

    output_dir = Path(s.KNOWLEDGE_BASE_PATH).parent
    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"  - Cannot create output directory {output_dir}: {e}")

    chroma_dir = Path(s.CHROMA_PERSIST_DIR)
    if not chroma_dir.exists():
        try:
            chroma_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"  - Cannot create chroma directory {chroma_dir}: {e}")

    if errors:
        print("\n[STARTUP ERROR] Configuration issues found:\n")
        for e in errors:
            print(e)
        print("\nFix the above before starting the server.\n")
        sys.exit(1)


settings = Settings()
_validate_settings(settings)