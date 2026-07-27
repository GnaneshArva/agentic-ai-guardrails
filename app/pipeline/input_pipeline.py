import time
from app.dto.enums import ExecutionMode
from app.dto.input import InputGuardrailRequest
from app.dto.results import PipelineResult
from app.interfaces.input_guardrail import InputGuardrail
from app.pipeline.base_pipeline import BaseGuardrailPipeline


class InputGuardrailPipeline(BaseGuardrailPipeline[InputGuardrailRequest, InputGuardrail]):
    """Chain of Responsibility Pipeline for processing Input Guardrails."""

    async def validate(self, request: InputGuardrailRequest) -> PipelineResult:
        """Executes all configured input guardrails and returns a unified PipelineResult.

        Public API:
            input_pipeline.validate(request)
        """
        start_time = time.perf_counter()

        if self._mode == ExecutionMode.PARALLEL:
            results, violations, action, is_allowed, sanitized_prompt = await self._execute_parallel(request)
        else:
            results, violations, action, is_allowed, sanitized_prompt = await self._execute_sequential(request)

        exec_time = (time.perf_counter() - start_time) * 1000.0

        return PipelineResult(
            is_allowed=is_allowed,
            action=action,
            violations=violations,
            sanitized_request=sanitized_prompt if is_allowed else None,
            sanitized_response=None,
            total_execution_time_ms=exec_time,
            guardrail_results=results,
        )
