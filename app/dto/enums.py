from enum import Enum


class GuardrailAction(str, Enum):
    """Action outcome from a guardrail execution."""
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    WARNING = "WARNING"


class ExecutionMode(str, Enum):
    """Pipeline execution strategy."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


class Severity(str, Enum):
    """Severity classification for guardrail violations."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PiiAction(str, Enum):
    """Action to take when PII is detected."""
    MASK = "MASK"
    REJECT = "REJECT"
    WARN = "WARN"
