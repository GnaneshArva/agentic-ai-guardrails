import time
from app.dto.enums import ExecutionMode
from app.dto.output import OutputGuardrailRequest
from app.dto.results import PipelineResult
from app.interfaces.output_guardrail import OutputGuardrail
from app.pipeline.base_pipeline import BaseGuardrailPipeline


class OutputGuardrailPipeline(BaseGuardrailPipeline[OutputGuardrailRequest, OutputGuardrail]):
    """Chain of Responsibility Pipeline for processing Output Guardrails."""

    async def validate(self, request: OutputGuardrailRequest) -> PipelineResult:
        """Executes all configured output guardrails and returns a unified PipelineResult.

        Public API:
            output_pipeline.validate(response)
        """
        start_time = time.perf_counter()

        if self._mode == ExecutionMode.PARALLEL:
            results, violations, action, is_allowed, sanitized_response = await self._execute_parallel(request)
        else:
            results, violations, action, is_allowed, sanitized_response = await self._execute_sequential(request)

        exec_time = (time.perf_counter() - start_time) * 1000.0

        return PipelineResult(
            is_allowed=is_allowed,
            action=action,
            violations=violations,
            sanitized_request=None,
            sanitized_response=sanitized_response if is_allowed else None,
            total_execution_time_ms=exec_time,
            guardrail_results=results,
        )
