import pytest
from app.dto.output import OutputGuardrailRequest
from app.dto.enums import GuardrailAction
from app.strategies.output.coherence import CoherenceGuardrail

@pytest.mark.anyio
async def test_coherence_guardrail_pass():
    guardrail = CoherenceGuardrail(min_coherence_score=0.70)
    coherent_text = (
        "Here is your 3-day Switzerland travel plan:\n\n"
        "Day 1: Arrival in Zurich and check-in at Grand Hotel Alpine.\n\n"
        "Day 2: Take scenic train ride to Lucerne and explore Old Town.\n\n"
        "Day 3: Day trip to Mount Titlis and afternoon return flight."
    )
    request = OutputGuardrailRequest(response_text=coherent_text)
    res = await guardrail.validate(request)

    assert res.guardrail_name == "CoherenceGuardrail"
    assert res.action == GuardrailAction.ALLOW
    assert res.score >= 0.70
    assert len(res.violations) == 0

@pytest.mark.anyio
async def test_coherence_guardrail_out_of_order_sequence_fail():
    guardrail = CoherenceGuardrail(min_coherence_score=0.70)
    incoherent_text = (
        "Day 3: Check out of hotel and departure flight.\n\n"
        "Day 1: Arrival in Tokyo.\n\n"
        "Day 2: City tour."
    )
    request = OutputGuardrailRequest(response_text=incoherent_text)
    res = await guardrail.validate(request)

    assert res.guardrail_name == "CoherenceGuardrail"
    assert len(res.violations) > 0
    assert "Coherence violation" in res.violations[0].message
