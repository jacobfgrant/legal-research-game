"""SQLAlchemy models for game state persistence."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from database import Base


class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(String, primary_key=True)
    scenario_id = Column(String, nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    hours_remaining = Column(Float, nullable=True)
    score_total = Column(Integer, nullable=True)
    score_relevance = Column(Integer, nullable=True)
    score_strength = Column(Integer, nullable=True)
    score_completeness = Column(Integer, nullable=True)
    score_efficiency = Column(Integer, nullable=True)


class SubmittedArgument(Base):
    __tablename__ = "submitted_arguments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("game_sessions.id"), nullable=False)
    slot_id = Column(String, nullable=False)
    authority_id = Column(String, nullable=False)
    authority_type = Column(String, nullable=False)


class SearchLog(Base):
    __tablename__ = "search_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("game_sessions.id"), nullable=False)
    query = Column(Text, nullable=False)
    results_count = Column(Integer, default=0)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
