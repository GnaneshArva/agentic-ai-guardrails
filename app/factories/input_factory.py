from typing import Optional
from app.config.settings import Settings, settings as global_settings
from app.interfaces.input_guardrail import InputGuardrail
from app.pipeline.input_pipeline import InputGuardrailPipeline
from app.strategies.input.business_input_validation import BusinessValidationGuardrail
from app.strategies.input.input_validation import InputValidationGuardrail
from app.strategies.input.jailbreak import JailbreakGuardrail
from app.strategies.input.pii_input import PiiInputGuardrail
from app.strategies.input.prompt_injection import PromptInjectionGuardrail


class InputGuardrailFactory:
    """Factory Pattern class to dynamically create InputGuardrailPipeline from Settings configuration."""

    @staticmethod
    def create_pipeline(
        cfg: Optional[Settings] = None,
        custom_guardrails: Optional[list[InputGuardrail]] = None,
    ) -> InputGuardrailPipeline:
        """Constructs an InputGuardrailPipeline configured according to settings.

        Args:
            cfg: Settings instance (defaults to global singleton if None)
            custom_guardrails: Additional custom InputGuardrail strategies to include

        Returns:
            InputGuardrailPipeline instance
        """
        active_settings = cfg or global_settings
        guardrails: list[InputGuardrail] = []

        if active_settings.ENABLE_PROMPT_INJECTION:
            guardrails.append(PromptInjectionGuardrail())

        if active_settings.ENABLE_JAILBREAK:
            guardrails.append(JailbreakGuardrail())

        if active_settings.ENABLE_PII_INPUT:
            guardrails.append(PiiInputGuardrail(action=active_settings.PII_INPUT_ACTION))

        if active_settings.ENABLE_INPUT_VALIDATION:
            guardrails.append(
                InputValidationGuardrail(
                    max_prompt_size_bytes=active_settings.MAX_PROMPT_SIZE_BYTES,
                    max_attachment_size_bytes=active_settings.MAX_ATTACHMENT_SIZE_BYTES,
                )
            )

        if active_settings.ENABLE_BUSINESS_INPUT:
            guardrails.append(BusinessValidationGuardrail())

        if custom_guardrails:
            guardrails.extend(custom_guardrails)

        return InputGuardrailPipeline(
            guardrails=guardrails,
            mode=active_settings.EXECUTION_MODE,
            stop_on_first_failure=active_settings.STOP_ON_FIRST_FAILURE,
        )
