import time
from app.dto.enums import GuardrailAction, Severity
from app.dto.input import InputGuardrailRequest
from app.dto.results import GuardrailResult, GuardrailViolation
from app.interfaces.input_guardrail import InputGuardrail
from app.utils.regex_patterns import PROMPT_INJECTION_PATTERNS


class PromptInjectionGuardrail(InputGuardrail):
    """Guardrail to detect prompt injection, system prompt leakage, and instruction overrides."""

    @property
    def name(self) -> str:
        return "PromptInjectionGuardrail"

    async def validate(self, request: InputGuardrailRequest) -> GuardrailResult:
        start_time = time.perf_counter()
        violations: list[GuardrailViolation] = []

        prompt_text = request.prompt
        if request.system_prompt:
            prompt_text += f"\n{request.system_prompt}"

        for pattern in PROMPT_INJECTION_PATTERNS:
            match = pattern.search(prompt_text)
            if match:
                violations.append(
                    GuardrailViolation(
                        guardrail_name=self.name,
                        message=f"Prompt injection attempt detected: '{match.group(0)}'",
                        severity=Severity.CRITICAL,
                        details={"matched_text": match.group(0), "pattern": pattern.pattern},
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
            sanitized_content=request.prompt,
            score=1.0,
            violations=[],
            execution_time_ms=exec_time,
        )
