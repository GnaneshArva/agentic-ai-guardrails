from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.dto.enums import ExecutionMode, PiiAction


class Settings(BaseSettings):
    """Centralized configuration for the Guardrails framework."""

    # Pipeline Execution Settings
    EXECUTION_MODE: ExecutionMode = Field(default=ExecutionMode.SEQUENTIAL, description="Pipeline execution mode: sequential or parallel")
    STOP_ON_FIRST_FAILURE: bool = Field(default=True, description="Whether sequential pipeline halts immediately on first blocking violation")

    # Input Guardrail Toggles
    ENABLE_PROMPT_INJECTION: bool = Field(default=True, description="Enable prompt injection detection")
    ENABLE_JAILBREAK: bool = Field(default=True, description="Enable jailbreak & DAN detection")
    ENABLE_PII_INPUT: bool = Field(default=True, description="Enable PII detection in input prompts")
    ENABLE_INPUT_VALIDATION: bool = Field(default=True, description="Enable standard input schema/size validation")
    ENABLE_BUSINESS_INPUT: bool = Field(default=True, description="Enable business domain validation on input")

    # Output Guardrail Toggles
    ENABLE_PII_OUTPUT: bool = Field(default=True, description="Enable PII detection & masking in LLM outputs")
    ENABLE_TOXICITY: bool = Field(default=True, description="Enable toxicity and offensive content detection")
    ENABLE_HALLUCINATION: bool = Field(default=True, description="Enable grounding hallucination checks")
    ENABLE_CITATION: bool = Field(default=True, description="Enable citation verification against context")
    ENABLE_STRUCTURED_OUTPUT: bool = Field(default=True, description="Enable structured output schema validation")
    ENABLE_BUSINESS_OUTPUT: bool = Field(default=True, description="Enable business domain validation on output")
    ENABLE_COHERENCE: bool = Field(default=True, description="Enable coherence and logical flow validation on output")

    # PII Handling Actions
    PII_INPUT_ACTION: PiiAction = Field(default=PiiAction.MASK, description="Action for input PII: MASK, REJECT, or WARN")
    PII_OUTPUT_ACTION: PiiAction = Field(default=PiiAction.MASK, description="Action for output PII: MASK, REJECT, or WARN")

    # Thresholds & Limits
    MAX_PROMPT_SIZE_BYTES: int = Field(default=102400, description="Max prompt size in bytes (default 100KB)")
    MAX_ATTACHMENT_SIZE_BYTES: int = Field(default=10485760, description="Max individual attachment size in bytes (default 10MB)")
    HALLUCINATION_MIN_GROUNDING_SCORE: float = Field(default=0.60, ge=0.0, le=1.0, description="Minimum grounding overlap score required")
    TOXICITY_THRESHOLD: float = Field(default=0.50, ge=0.0, le=1.0, description="Toxicity detection score threshold")
    COHERENCE_MIN_SCORE: float = Field(default=0.70, ge=0.0, le=1.0, description="Minimum coherence score required")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# Singleton settings instance
settings = Settings()
