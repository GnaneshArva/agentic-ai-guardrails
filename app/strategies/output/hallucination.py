import time
import re
from app.dto.enums import GuardrailAction, Severity
from app.dto.output import OutputGuardrailRequest
from app.dto.results import GuardrailResult, GuardrailViolation
from app.interfaces.output_guardrail import OutputGuardrail


class HallucinationGuardrail(OutputGuardrail):
    """Guardrail to verify output grounding against retrieved RAG context.
    
    Default implementation uses keyword/token overlap grounding metric.
    Designed to be subclassed or swapped with LLM-as-a-Judge or External Fact Verifiers.
    """

    def __init__(self, min_grounding_score: float = 0.60):
        self._min_grounding_score = min_grounding_score

    @property
    def name(self) -> str:
        return "HallucinationGuardrail"

    async def validate(self, request: OutputGuardrailRequest) -> GuardrailResult:
        start_time = time.perf_counter()
        violations: list[GuardrailViolation] = []

        # If no context is provided, grounding verification is skipped with full score
        if not request.retrieved_context:
            exec_time = (time.perf_counter() - start_time) * 1000.0
            return GuardrailResult(
                guardrail_name=self.name,
                action=GuardrailAction.ALLOW,
                sanitized_content=request.response_text,
                score=1.0,
                violations=[],
                execution_time_ms=exec_time,
            )

        # Grounding check: measure overlap of key words between response and retrieved context
        context_corpus = " ".join(request.retrieved_context).lower()
        context_words = set(re.findall(r"\b[a-z0-9]{3,}\b", context_corpus))

        response_words = re.findall(r"\b[a-z0-9]{3,}\b", request.response_text.lower())
        if not response_words:
            grounding_score = 1.0
        else:
            supported_words = [w for w in response_words if w in context_words]
            grounding_score = len(supported_words) / len(response_words)

        exec_time = (time.perf_counter() - start_time) * 1000.0

        if grounding_score < self._min_grounding_score:
            violations.append(
                GuardrailViolation(
                    guardrail_name=self.name,
                    message=f"Low grounding score ({grounding_score:.2f} < {self._min_grounding_score:.2f}). Output may contain hallucinations.",
                    severity=Severity.HIGH,
                    details={"grounding_score": grounding_score, "min_required": self._min_grounding_score},
                )
            )
            return GuardrailResult(
                guardrail_name=self.name,
                action=GuardrailAction.BLOCK,
                sanitized_content=None,
                score=grounding_score,
                violations=violations,
                execution_time_ms=exec_time,
            )

        return GuardrailResult(
            guardrail_name=self.name,
            action=GuardrailAction.ALLOW,
            sanitized_content=request.response_text,
            score=grounding_score,
            violations=[],
            execution_time_ms=exec_time,
        )
