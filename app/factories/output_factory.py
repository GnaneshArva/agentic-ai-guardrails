from typing import Optional
from app.config.settings import Settings, settings as global_settings
from app.interfaces.output_guardrail import OutputGuardrail
from app.pipeline.output_pipeline import OutputGuardrailPipeline
from app.strategies.output.business_output_validation import BusinessOutputGuardrail
from app.strategies.output.citation import CitationGuardrail
from app.strategies.output.coherence import CoherenceGuardrail
from app.strategies.output.hallucination import HallucinationGuardrail
from app.strategies.output.pii_output import PiiOutputGuardrail
from app.strategies.output.structured_output import StructuredOutputGuardrail
from app.strategies.output.toxicity import ToxicityGuardrail


class OutputGuardrailFactory:
    """Factory Pattern class to dynamically create OutputGuardrailPipeline from Settings configuration."""

    @staticmethod
    def create_pipeline(
        cfg: Optional[Settings] = None,
        custom_guardrails: Optional[list[OutputGuardrail]] = None,
    ) -> OutputGuardrailPipeline:
        """Constructs an OutputGuardrailPipeline configured according to settings.

        Args:
            cfg: Settings instance (defaults to global singleton if None)
            custom_guardrails: Additional custom OutputGuardrail strategies to include

        Returns:
            OutputGuardrailPipeline instance
        """
        active_settings = cfg or global_settings
        guardrails: list[OutputGuardrail] = []

        if active_settings.ENABLE_PII_OUTPUT:
            guardrails.append(PiiOutputGuardrail(action=active_settings.PII_OUTPUT_ACTION))

        if active_settings.ENABLE_TOXICITY:
            guardrails.append(ToxicityGuardrail(threshold=active_settings.TOXICITY_THRESHOLD))

        if active_settings.ENABLE_HALLUCINATION:
            guardrails.append(
                HallucinationGuardrail(min_grounding_score=active_settings.HALLUCINATION_MIN_GROUNDING_SCORE)
            )

        if active_settings.ENABLE_CITATION:
            guardrails.append(CitationGuardrail())

        if active_settings.ENABLE_STRUCTURED_OUTPUT:
            guardrails.append(StructuredOutputGuardrail())

        if active_settings.ENABLE_BUSINESS_OUTPUT:
            guardrails.append(BusinessOutputGuardrail())

        if active_settings.ENABLE_COHERENCE:
            guardrails.append(CoherenceGuardrail(min_coherence_score=active_settings.COHERENCE_MIN_SCORE))

        if custom_guardrails:
            guardrails.extend(custom_guardrails)

        return OutputGuardrailPipeline(
            guardrails=guardrails,
            mode=active_settings.EXECUTION_MODE,
            stop_on_first_failure=active_settings.STOP_ON_FIRST_FAILURE,
        )
