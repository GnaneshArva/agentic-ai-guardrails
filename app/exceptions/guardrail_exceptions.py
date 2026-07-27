class GuardrailException(Exception):
    """Base exception for all guardrail framework errors."""
    pass


class GuardrailConfigurationError(GuardrailException):
    """Raised when configuration or settings initialization fails."""
    pass


class GuardrailPipelineError(GuardrailException):
    """Raised when pipeline execution fails due to unexpected errors."""
    pass
