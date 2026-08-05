import time
import re
from typing import List, Dict, Any
from app.dto.enums import GuardrailAction, Severity
from app.dto.output import OutputGuardrailRequest
from app.dto.results import GuardrailResult, GuardrailViolation
from app.interfaces.output_guardrail import OutputGuardrail


class RiskAssessmentGuardrail(OutputGuardrail):
    """Output Guardrail evaluating action risk level and Human-in-the-Loop (HITL) approval requirements.
    
    Risk Matrix:
    - LOW: Read-only search, itinerary generation, RAG doc retrieval (Auto-continue).
    - MEDIUM: Advisory notes, weather re-planning suggestions (Optional confirmation).
    - HIGH / CRITICAL: Flight/Hotel bookings, payment processing, budget overrides, cancellations (Mandatory HITL Approval).
    """

    def __init__(self, auto_approval_max_amount_usd: float = 250.0):
        self._max_auto_amount = auto_approval_max_amount_usd

    @property
    def name(self) -> str:
        return "RiskAssessmentGuardrail"

    async def validate(self, request: OutputGuardrailRequest) -> GuardrailResult:
        start_time = time.perf_counter()
        violations: List[GuardrailViolation] = []
        text = request.response_text.lower()
        tool_calls = request.tool_calls or []

        risk_level = "LOW"
        requires_approval = False
        reasons: List[str] = []

        # 1. Inspect Tool Calls for High-Risk External Actions
        high_risk_tools = ["book_flight", "book_hotel", "execute_payment", "cancel_booking", "override_budget"]
        for tool in tool_calls:
            t_name = str(tool.get("tool_name", "") or tool.get("name", "")).lower()
            t_args = tool.get("args", {}) or tool.get("parameters", {}) or {}
            
            if any(hrt in t_name for hrt in high_risk_tools):
                risk_level = "CRITICAL"
                requires_approval = True
                reasons.append(f"Invocation of sensitive external action tool: '{t_name}'.")

            # Check financial amount
            amount = float(t_args.get("amount", 0.0) or t_args.get("price", 0.0) or 0.0)
            if amount > self._max_auto_amount:
                risk_level = "CRITICAL"
                requires_approval = True
                reasons.append(f"Financial amount (${amount:.2f}) exceeds auto-approval threshold (${self._max_auto_amount:.2f}).")

        # 2. Text Keyword Heuristics for Implicit Booking / Payment Intent
        booking_keywords = ["confirmed booking", "booked flight", "booked hotel", "charged your card", "payment processed", "cancellation confirmed"]
        if any(kw in text for kw in booking_keywords):
            if risk_level != "CRITICAL":
                risk_level = "HIGH"
            requires_approval = True
            reasons.append("Response text references completed binding booking or payment transaction.")

        # Extract monetary amounts in text (e.g. $500, USD 600, ₹50,000)
        prices = [float(p) for p in re.findall(r"\$(?:USD)?\s*(\d+(?:\.\d+)?)\b", request.response_text)]
        for price in prices:
            if price > self._max_auto_amount * 2:
                if risk_level == "LOW":
                    risk_level = "HIGH"
                requires_approval = True
                reasons.append(f"High financial transaction amount detected in output text (${price:.2f}).")

        exec_time = (time.perf_counter() - start_time) * 1000.0

        if requires_approval:
            msg = "; ".join(reasons) if reasons else "High-risk action requires human approval."
            violations.append(
                GuardrailViolation(
                    guardrail_name=self.name,
                    message=f"HITL Approval Required [{risk_level}]: {msg}",
                    severity=Severity.HIGH,
                    details={
                        "risk_level": risk_level,
                        "requires_human_approval": True,
                        "reasons": reasons,
                        "auto_approval_max_amount_usd": self._max_auto_amount
                    },
                )
            )
            return GuardrailResult(
                guardrail_name=self.name,
                action=GuardrailAction.WARNING,
                sanitized_content=request.response_text,
                score=0.40 if risk_level == "CRITICAL" else 0.60,
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
