"""
CodeAgent Python Executors.

This module provides different execution backends for running Python code.
"""

from .base import (
    BaseToolWrapper,
    CodeOutput,
    FinalAnswerException,
    PythonExecutor,
    wrap_final_answer,
)
from .local_executor import (
    LocalPythonExecutor,
    create_default_final_answer,
    create_local_executor,
    truncate_text,
)
from .docker_executor import (
    DockerPythonExecutor,
    create_docker_executor,
)
from .backend_executor import (
    BackendPythonExecutor,
)
from .router import (
    ExecutorRouter,
    SecurityError,
    create_router,
    DANGEROUS_PATTERNS,
    DATA_ANALYSIS_PATTERNS,
)

__all__ = [
    # Base types
    "CodeOutput",
    "FinalAnswerException",
    "PythonExecutor",
    "BaseToolWrapper",
    "wrap_final_answer",
    # Local executor
    "LocalPythonExecutor",
    "create_local_executor",
    "create_default_final_answer",
    "truncate_text",
    # Docker executor
    "DockerPythonExecutor",
    "create_docker_executor",
    # Backend executor
    "BackendPythonExecutor",
    # Router
    "ExecutorRouter",
    "SecurityError",
    "create_router",
    "DANGEROUS_PATTERNS",
    "DATA_ANALYSIS_PATTERNS",
]

