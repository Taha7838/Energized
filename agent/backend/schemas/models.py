# backend/schemas/models.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class QueryRequest(BaseModel):
    query: str


class ResearchResult(BaseModel):
    query: str
    summary: str
    sources: list[str]
    timestamp: str
    from_cache: bool


class HistoryItem(BaseModel):
    query: str
    summary: str
    sources: list[str]
    timestamp: str
    from_cache: bool


class HistoryResponse(BaseModel):
    items: list[HistoryItem]