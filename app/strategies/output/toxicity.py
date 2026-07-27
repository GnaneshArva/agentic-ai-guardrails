import time
from app.dto.enums import GuardrailAction, Severity
from app.dto.output import OutputGuardrailRequest
from app.dto.results import GuardrailResult, GuardrailViolation
from app.interfaces.output_guardrail import OutputGuardrail
from app.utils.regex_patterns import TOXICITY_PATTERNS


class ToxicityGuardrail(OutputGuardrail):
    """Guardrail to detect hate speech, abuse, harassment, and offensive language in LLM output."""

    def __init__(self, threshold: float = 0.50):
        self._threshold = threshold

    @property
    def name(self) -> str:
        return "ToxicityGuardrail"

    async def validate(self, request: OutputGuardrailRequest) -> GuardrailResult:
        start_time = time.perf_counter()
        violations: list[GuardrailViolation] = []

        response_text = request.response_text

        for pattern in TOXICITY_PATTERNS:
            match = pattern.search(response_text)
            if match:
                violations.append(
                    GuardrailViolation(
                        guardrail_name=self.name,
                        message=f"Toxicity / abusive content detected: '{match.group(0)}'",
                        severity=Severity.HIGH,
                        details={"matched_text": match.group(0)},
                    )
                )

        exec_time = (time.perf_counter() - start_time) * 1000.0

        if violations:
            return GuardrailResult(
                guardrail_name=self.name,
                action=GuardrailAction.BLOCK,
                sanitized_content=None,
                score=0.0,
                violations=violations,
                execution_time_ms=exec_time,
            )

        return GuardrailResult(
            guardrail_name=self.name,
            action=GuardrailAction.ALLOW,
            sanitized_content=request.response_text,
            score=1.0,
            violations=[],
            execution_time_ms=exec_time,
        )
