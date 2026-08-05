import pytest
from app.dto.output import OutputGuardrailRequest
from app.dto.enums import GuardrailAction
from app.strategies.output.risk_assessment import RiskAssessmentGuardrail

@pytest.mark.anyio
async def test_risk_assessment_search_low_risk_auto_pass():
    guardrail = RiskAssessmentGuardrail(auto_approval_max_amount_usd=250.0)
    request = OutputGuardrailRequest(
        response_text="Here are the searched flight options to Tokyo.",
        tool_calls=[{"tool_name": "search_flights", "args": {"destination": "Tokyo"}}]
    )
    res = await guardrail.validate(request)
    assert res.guardrail_name == "RiskAssessmentGuardrail"
    assert res.action == GuardrailAction.ALLOW
    assert len(res.violations) == 0

@pytest.mark.anyio
async def test_risk_assessment_book_flight_high_risk_hitl_required():
    guardrail = RiskAssessmentGuardrail(auto_approval_max_amount_usd=250.0)
    request = OutputGuardrailRequest(
        response_text="Confirmed booking for flight SQ-638 for $650.00.",
        tool_calls=[{"tool_name": "book_flight", "args": {"flight_id": "SQ-638", "amount": 650.00}}]
    )
    res = await guardrail.validate(request)
    assert res.guardrail_name == "RiskAssessmentGuardrail"
    assert res.action == GuardrailAction.WARNING
    assert len(res.violations) > 0
    assert res.violations[0].details["requires_human_approval"] is True
    assert res.violations[0].details["risk_level"] == "CRITICAL"
