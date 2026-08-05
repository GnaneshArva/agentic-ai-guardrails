import time
import unicodedata
from app.dto.enums import GuardrailAction
from app.dto.input import InputGuardrailRequest
from app.dto.results import GuardrailResult
from app.interfaces.input_guardrail import InputGuardrail


class UnicodeNormalizationGuardrail(InputGuardrail):
    """Guardrail enforcing NFKC unicode normalization to prevent homoglyph & character obfuscation attacks."""

    @property
    def name(self) -> str:
        return "UnicodeNormalizationGuardrail"

    async def validate(self, request: InputGuardrailRequest) -> GuardrailResult:
        start_time = time.perf_counter()
        original_prompt = request.prompt
        
        # Apply NFKC Unicode Normalization
        normalized_prompt = unicodedata.normalize("NFKC", original_prompt)
        exec_time = (time.perf_counter() - start_time) * 1000.0

        return GuardrailResult(
            guardrail_name=self.name,
            action=GuardrailAction.ALLOW,
            sanitized_content=normalized_prompt,
            score=1.0,
            violations=[],
            execution_time_ms=exec_time,
        )
