import time
from app.dto.enums import GuardrailAction, PiiAction, Severity
from app.dto.output import OutputGuardrailRequest
from app.dto.results import GuardrailResult, GuardrailViolation
from app.interfaces.output_guardrail import OutputGuardrail
from app.utils.regex_patterns import (
    API_KEY_PATTERN,
    CREDIT_CARD_PATTERN,
    EMAIL_PATTERN,
    PASSPORT_PATTERN,
    PASSWORD_PATTERN,
    PHONE_PATTERN,
)


class PiiOutputGuardrail(OutputGuardrail):
    """Guardrail to sanitize or block PII (Credit Cards, Passports, Emails, Phones, Secrets) in LLM responses."""

    def __init__(self, action: PiiAction = PiiAction.MASK):
        self._action = action

    @property
    def name(self) -> str:
        return "PiiOutputGuardrail"

    async def validate(self, request: OutputGuardrailRequest) -> GuardrailResult:
        start_time = time.perf_counter()
        violations: list[GuardrailViolation] = []
        sanitized_response = request.response_text

        pii_checks = [
            ("Credit Card", CREDIT_CARD_PATTERN, "[REDACTED_CREDIT_CARD]"),
            ("Passport", PASSPORT_PATTERN, "[REDACTED_PASSPORT]"),
            ("Email", EMAIL_PATTERN, "[REDACTED_EMAIL]"),
            ("Phone", PHONE_PATTERN, "[REDACTED_PHONE]"),
            ("API Key", API_KEY_PATTERN, "[REDACTED_API_KEY]"),
            ("Secret/Password", PASSWORD_PATTERN, "password=[REDACTED_SECRET]"),
        ]

        for pii_type, pattern, replacement in pii_checks:
            matches = list(pattern.finditer(sanitized_response))
            if matches:
                violations.append(
                    GuardrailViolation(
                        guardrail_name=self.name,
                        message=f"PII ({pii_type}) detected in output response",
                        severity=Severity.HIGH if self._action == PiiAction.REJECT else Severity.MEDIUM,
                        details={"pii_type": pii_type, "count": len(matches)},
                    )
                )
                if self._action == PiiAction.MASK:
                    sanitized_response = pattern.sub(replacement, sanitized_response)

        exec_time = (time.perf_counter() - start_time) * 1000.0

        if not violations:
            return GuardrailResult(
                guardrail_name=self.name,
                action=GuardrailAction.ALLOW,
                sanitized_content=request.response_text,
                score=1.0,
                violations=[],
                execution_time_ms=exec_time,
            )

        if self._action == PiiAction.REJECT:
            return GuardrailResult(
                guardrail_name=self.name,
                action=GuardrailAction.BLOCK,
                sanitized_content=None,
                score=0.0,
                violations=violations,
                execution_time_ms=exec_time,
            )
        elif self._action == PiiAction.WARN:
            return GuardrailResult(
                guardrail_name=self.name,
                action=GuardrailAction.WARNING,
                sanitized_content=request.response_text,
                score=0.5,
                violations=violations,
                execution_time_ms=exec_time,
            )
        else:  # MASK
            return GuardrailResult(
                guardrail_name=self.name,
                action=GuardrailAction.ALLOW,
                sanitized_content=sanitized_response,
                score=0.8,
                violations=violations,
                execution_time_ms=exec_time,
            )
