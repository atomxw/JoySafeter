"""
Memory subsystem for the core agent.

Note: Use local/core import paths (app.core.agent...) instead of the legacy
app.agent... package layout.
"""

from app.schemas.memory import UserMemory

from .manager import MemoryManager
from .strategies import (
    MemoryOptimizationStrategy,
    MemoryOptimizationStrategyFactory,
    MemoryOptimizationStrategyType,
    SummarizeStrategy,
)

__all__ = [
    "MemoryManager",
    "UserMemory",
    "MemoryOptimizationStrategy",
    "MemoryOptimizationStrategyType",
    "MemoryOptimizationStrategyFactory",
    "SummarizeStrategy",
]
