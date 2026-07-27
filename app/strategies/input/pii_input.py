import time
from typing import Optional
from app.dto.enums import GuardrailAction, PiiAction, Severity
from app.dto.input import InputGuardrailRequest
from app.dto.results import GuardrailResult, GuardrailViolation
from app.interfaces.input_guardrail import InputGuardrail
from app.utils.regex_patterns import (
    AADHAAR_PATTERN,
    API_KEY_PATTERN,
    CREDIT_CARD_PATTERN,
    PAN_PATTERN,
    PASSPORT_PATTERN,
    PASSWORD_PATTERN,
    SSN_PATTERN,
)


class PiiInputGuardrail(InputGuardrail):
    """Guardrail to detect and handle PII (Credit Cards, Passport, Aadhaar, PAN, SSN, API Keys, Passwords) in input prompts."""

    def __init__(self, action: PiiAction = PiiAction.MASK):
        self._action = action

    @property
    def name(self) -> str:
        return "PiiInputGuardrail"

    async def validate(self, request: InputGuardrailRequest) -> GuardrailResult:
        start_time = time.perf_counter()
        violations: list[GuardrailViolation] = []
        sanitized_prompt = request.prompt

        pii_checks = [
            ("Credit Card", CREDIT_CARD_PATTERN, "[REDACTED_CREDIT_CARD]"),
            ("SSN", SSN_PATTERN, "[REDACTED_SSN]"),
            ("Aadhaar", AADHAAR_PATTERN, "[REDACTED_AADHAAR]"),
            ("PAN Card", PAN_PATTERN, "[REDACTED_PAN]"),
            ("Passport", PASSPORT_PATTERN, "[REDACTED_PASSPORT]"),
            ("API Key", API_KEY_PATTERN, "[REDACTED_API_KEY]"),
            ("Password", PASSWORD_PATTERN, "password=[REDACTED_PASSWORD]"),
        ]

        for pii_type, pattern, replacement in pii_checks:
            matches = list(pattern.finditer(sanitized_prompt))
            if matches:
                violations.append(
                    GuardrailViolation(
                        guardrail_name=self.name,
                        message=f"PII ({pii_type}) detected in input prompt",
                        severity=Severity.HIGH if self._action == PiiAction.REJECT else Severity.MEDIUM,
                        details={"pii_type": pii_type, "count": len(matches)},
                    )
                )
                if self._action == PiiAction.MASK:
                    sanitized_prompt = pattern.sub(replacement, sanitized_prompt)

        exec_time = (time.perf_counter() - start_time) * 1000.0

        if not violations:
            return GuardrailResult(
                guardrail_name=self.name,
                action=GuardrailAction.ALLOW,
                sanitized_content=request.prompt,
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
                sanitized_content=request.prompt,
                score=0.5,
                violations=violations,
                execution_time_ms=exec_time,
            )
        else:  # MASK
            return GuardrailResult(
                guardrail_name=self.name,
                action=GuardrailAction.ALLOW,
                sanitized_content=sanitized_prompt,
                score=0.8,
                violations=violations,
                execution_time_ms=exec_time,
            )
