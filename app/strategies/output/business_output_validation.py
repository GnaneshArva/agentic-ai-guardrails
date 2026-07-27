import time
from typing import Callable, Optional
from app.dto.enums import GuardrailAction, Severity
from app.dto.output import OutputGuardrailRequest
from app.dto.results import GuardrailResult, GuardrailViolation
from app.interfaces.output_guardrail import OutputGuardrail

# Type alias for output business rule functions: returns list of violation messages if failed
OutputBusinessRuleFunc = Callable[[OutputGuardrailRequest], list[str]]


class BusinessOutputGuardrail(OutputGuardrail):
    """Pluggable business output validator enforcing domain invariants post-generation."""

    def __init__(self, rules: Optional[list[OutputBusinessRuleFunc]] = None):
        self._rules = rules or [self._default_output_business_rules]

    @property
    def name(self) -> str:
        return "BusinessOutputGuardrail"

    @staticmethod
    def _default_output_business_rules(request: OutputGuardrailRequest) -> list[str]:
        """Default business output rule: verify refund/payment claims match actual tool execution results."""
        violations = []
        response_lower = request.response_text.lower()

        if "refund approved" in response_lower or "refund processed" in response_lower:
            # Inspect tool_calls to check if payment/refund tool executed with success
            refund_tool_executed = False
            refund_tool_approved = False

            for tool_call in request.tool_calls:
                tool_name = tool_call.get("name", "").lower()
                if "payment" in tool_name or "refund" in tool_name:
                    refund_tool_executed = True
                    status = str(tool_call.get("status", "")).lower()
                    if status in ["success", "approved", "completed"]:
                        refund_tool_approved = True

            if not refund_tool_executed or not refund_tool_approved:
                violations.append(
                    "Business Output Violation: LLM declared 'Refund Approved' without a verified successful payment/refund tool execution."
                )

        return violations

    async def validate(self, request: OutputGuardrailRequest) -> GuardrailResult:
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
                        details={"rule": rule.__name__ if hasattr(rule, "__name__") else "custom_output_rule"},
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
