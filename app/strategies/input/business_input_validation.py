import time
from typing import Callable, Optional
from app.dto.enums import GuardrailAction, Severity
from app.dto.input import InputGuardrailRequest
from app.dto.results import GuardrailResult, GuardrailViolation
from app.interfaces.input_guardrail import InputGuardrail

# Type alias for custom business rule functions: returns list of violation messages if failed
BusinessRuleFunc = Callable[[InputGuardrailRequest], list[str]]


class BusinessValidationGuardrail(InputGuardrail):
    """Pluggable business rule validator for domain-specific input checks."""

    def __init__(self, rules: Optional[list[BusinessRuleFunc]] = None):
        self._rules = rules or [self._default_business_rules]

    @property
    def name(self) -> str:
        return "BusinessValidationGuardrail"

    @staticmethod
    def _default_business_rules(request: InputGuardrailRequest) -> list[str]:
        """Default business rules preventing unauthorized domain actions (e.g. HR/payroll access in Travel Agent context)."""
        prompt_lower = request.prompt.lower()
        forbidden_intents = [
            ("delete payroll", "Attempting unauthorized operation: delete payroll"),
            ("modify employee salary", "Attempting unauthorized operation: modify employee salary"),
            ("access hr database", "Attempting unauthorized operation: access HR database"),
            ("drop database", "Attempting unauthorized database deletion"),
            ("export user credentials", "Attempting unauthorized credential export"),
        ]

        violations = []
        for phrase, msg in forbidden_intents:
            if phrase in prompt_lower:
                violations.append(msg)
        return violations

    async def validate(self, request: InputGuardrailRequest) -> GuardrailResult:
        start_time = time.perf_counter()
        violations: list[GuardrailViolation] = []

        for rule in self._rules:
            rule_violations = rule(request)
            for err in rule_violations:
                violations.append(
                    GuardrailViolation(
                        guardrail_name=self.name,
                        message=err,
                        severity=Severity.HIGH,
                        details={"rule": rule.__name__ if hasattr(rule, "__name__") else "custom_rule"},
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
