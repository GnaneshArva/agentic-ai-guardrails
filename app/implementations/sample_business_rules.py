from app.dto.input import InputGuardrailRequest
from app.dto.output import OutputGuardrailRequest


def travel_agent_input_rule(request: InputGuardrailRequest) -> list[str]:
    """Sample custom business input rule for Travel Agent AI."""
    violations = []
    forbidden_terms = ["delete payroll", "override travel budget limit", "book executive class without approval"]
    prompt_lower = request.prompt.lower()

    for term in forbidden_terms:
        if term in prompt_lower:
            violations.append(f"Travel Agent Policy Violation: Unauthorized operation '{term}' detected.")
    return violations


def travel_agent_output_rule(request: OutputGuardrailRequest) -> list[str]:
    """Sample custom business output rule for Travel Agent AI."""
    violations = []
    if "booking confirmed" in request.response_text.lower():
        booking_tool_present = any("booking" in t.get("name", "").lower() for t in request.tool_calls)
        if not booking_tool_present:
            violations.append("Travel Agent Output Violation: 'Booking Confirmed' statement issued without active booking tool execution.")
    return violations
