from typing import Any, Optional
from pydantic import BaseModel, Field


class AttachmentMetadata(BaseModel):
    """Metadata describing a file or data attachment provided with the input."""
    filename: str = Field(..., description="Name of attached file")
    mime_type: str = Field(..., description="MIME content type")
    size_bytes: int = Field(..., ge=0, description="Size of attachment in bytes")


class InputGuardrailRequest(BaseModel):
    """Input payload sent to the Input Guardrail Pipeline prior to LLM execution."""
    prompt: str = Field(..., description="Raw prompt text from user or client")
    user_id: Optional[str] = Field(default=None, description="Unique identifier for the user requesting inference")
    session_id: Optional[str] = Field(default=None, description="Session or conversation tracking ID")
    system_prompt: Optional[str] = Field(default=None, description="System prompt or persona instructions")
    attachments: list[AttachmentMetadata] = Field(default_factory=list, description="Associated file attachments")
    custom_rules: list[str] = Field(default_factory=list, description="Custom business rule identifiers or parameters")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary request context metadata")
