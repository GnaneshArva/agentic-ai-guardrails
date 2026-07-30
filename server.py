"""
FastAPI HTTP Server for agentic-ai-guardrails.

Exposes the GuardrailService facade as REST endpoints so that
travel-agent-service (and other microservices) can call guardrails
over HTTP at the configured GUARDRAILS_SERVICE_URL (default :8004).

Run with:
    uvicorn server:app --host 0.0.0.0 --port 8004
"""

from typing import Any, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI

from app.services.guardrail_service import GuardrailService
from app.dto.input import InputGuardrailRequest
from app.dto.output import OutputGuardrailRequest

app = FastAPI(
    title="Agentic AI Guardrails Service",
    description="Enterprise-grade Input & Output Guardrails for Agentic AI systems",
    version="0.1.0",
)

service = GuardrailService()


# ── Request / Response DTOs for the HTTP layer ──────────────────────────────

class InputValidationRequest(BaseModel):
    """HTTP request body for input validation."""
    text: str = Field(..., description="Raw prompt text to validate")
    session_id: Optional[str] = Field(default=None, description="Session tracking ID")


class OutputValidationRequest(BaseModel):
    """HTTP request body for output validation."""
    text: str = Field(..., description="LLM response text to validate")
    session_id: Optional[str] = Field(default=None, description="Session tracking ID")
    retrieved_context: list[str] = Field(default_factory=list, description="RAG context for grounding checks")


class ValidationResponse(BaseModel):
    """Standardised HTTP response returned by both input and output endpoints."""
    is_allowed: bool
    sanitized_text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


# ── Endpoints ───────────────────────────────────────────────────────────────

@app.post("/guardrails/input/validate", response_model=ValidationResponse)
async def validate_input(req: InputValidationRequest) -> ValidationResponse:
    """Run the full Input Guardrail Pipeline on the supplied text."""
    guardrail_req = InputGuardrailRequest(prompt=req.text, session_id=req.session_id)
    result = await service.validate_input(guardrail_req)

    sanitized = result.sanitized_request if result.sanitized_request else req.text

    return ValidationResponse(
        is_allowed=result.is_allowed,
        sanitized_text=sanitized,
        metadata={
            "action": result.action.value,
            "violations": [v.model_dump() for v in result.violations],
            "execution_time_ms": result.total_execution_time_ms,
            "guardrail_results": [r.model_dump() for r in result.guardrail_results],
        },
    )


@app.post("/guardrails/output/validate", response_model=ValidationResponse)
async def validate_output(req: OutputValidationRequest) -> ValidationResponse:
    """Run the full Output Guardrail Pipeline on the supplied text."""
    guardrail_req = OutputGuardrailRequest(
        response_text=req.text,
        retrieved_context=req.retrieved_context,
    )
    result = await service.validate_output(guardrail_req)

    sanitized = result.sanitized_response if result.sanitized_response else req.text

    return ValidationResponse(
        is_allowed=result.is_allowed,
        sanitized_text=sanitized,
        metadata={
            "action": result.action.value,
            "violations": [v.model_dump() for v in result.violations],
            "execution_time_ms": result.total_execution_time_ms,
            "guardrail_results": [r.model_dump() for r in result.guardrail_results],
        },
    )


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "agentic-ai-guardrails"}
