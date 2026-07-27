from abc import ABC, abstractmethod
from app.dto.input import InputGuardrailRequest
from app.dto.results import GuardrailResult


class InputGuardrail(ABC):
    """Abstract Strategy Interface for all Input Guardrails."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier name for this input guardrail."""
        pass

    @abstractmethod
    async def validate(self, request: InputGuardrailRequest) -> GuardrailResult:
        """Validate input prompt request.

        Args:
            request: DTO containing prompt, attachments, user details, and metadata.

        Returns:
            GuardrailResult DTO detailing action, score, violations, and sanitized content.
        """
        pass
