from abc import ABC, abstractmethod
from app.dto.output import OutputGuardrailRequest
from app.dto.results import GuardrailResult


class OutputGuardrail(ABC):
    """Abstract Strategy Interface for all Output Guardrails."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier name for this output guardrail."""
        pass

    @abstractmethod
    async def validate(self, request: OutputGuardrailRequest) -> GuardrailResult:
        """Validate LLM response output.

        Args:
            request: DTO containing generated text, retrieved context, citations, and schemas.

        Returns:
            GuardrailResult DTO detailing action, score, violations, and sanitized response.
        """
        pass
