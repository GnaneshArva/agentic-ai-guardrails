import asyncio
import time
from typing import Generic, TypeVar
from app.dto.enums import ExecutionMode, GuardrailAction
from app.dto.results import GuardrailResult, GuardrailViolation, PipelineResult

TRequest = TypeVar("TRequest")
TGuardrail = TypeVar("TGuardrail")


class BaseGuardrailPipeline(Generic[TRequest, TGuardrail]):
    """Base pipeline implementing Chain of Responsibility (Sequential with optional early stopping) and Parallel execution modes."""

    def __init__(
        self,
        guardrails: list[TGuardrail],
        mode: ExecutionMode = ExecutionMode.SEQUENTIAL,
        stop_on_first_failure: bool = True,
    ):
        self._guardrails = guardrails
        self._mode = mode
        self._stop_on_first_failure = stop_on_first_failure

    @property
    def guardrails(self) -> list[TGuardrail]:
        return self._guardrails

    @property
    def mode(self) -> ExecutionMode:
        return self._mode

    @property
    def stop_on_first_failure(self) -> bool:
        return self._stop_on_first_failure

    async def _execute_sequential(self, request: TRequest) -> tuple[list[GuardrailResult], list[GuardrailViolation], GuardrailAction, bool, any]:
        results: list[GuardrailResult] = []
        all_violations: list[GuardrailViolation] = []
        overall_action = GuardrailAction.ALLOW
        current_payload = request
        is_blocked = False

        for guardrail in self._guardrails:
            # Execute guardrail strategy
            res: GuardrailResult = await guardrail.validate(current_payload)
            results.append(res)
            all_violations.extend(res.violations)

            # If sanitized payload produced, pass to next guardrail in chain
            if res.sanitized_content is not None and hasattr(current_payload, "model_copy"):
                if hasattr(current_payload, "prompt"):
                    current_payload = current_payload.model_copy(update={"prompt": res.sanitized_content})
                elif hasattr(current_payload, "response_text"):
                    current_payload = current_payload.model_copy(update={"response_text": res.sanitized_content})

            if res.action == GuardrailAction.BLOCK:
                overall_action = GuardrailAction.BLOCK
                is_blocked = True
                if self._stop_on_first_failure:
                    # Early termination according to Chain of Responsibility pattern
                    break
            elif res.action == GuardrailAction.WARNING and overall_action != GuardrailAction.BLOCK:
                overall_action = GuardrailAction.WARNING

        final_sanitized = getattr(current_payload, "prompt", None) or getattr(current_payload, "response_text", None)
        return results, all_violations, overall_action, not is_blocked, final_sanitized

    async def _execute_parallel(self, request: TRequest) -> tuple[list[GuardrailResult], list[GuardrailViolation], GuardrailAction, bool, any]:
        # Execute all guardrails concurrently using asyncio.gather
        tasks = [guardrail.validate(request) for guardrail in self._guardrails]
        results: list[GuardrailResult] = await asyncio.gather(*tasks)

        all_violations: list[GuardrailViolation] = []
        overall_action = GuardrailAction.ALLOW
        is_blocked = False
        final_sanitized = getattr(request, "prompt", None) or getattr(request, "response_text", None)

        for res in results:
            all_violations.extend(res.violations)
            if res.sanitized_content is not None and res.action == GuardrailAction.ALLOW:
                final_sanitized = res.sanitized_content

            if res.action == GuardrailAction.BLOCK:
                overall_action = GuardrailAction.BLOCK
                is_blocked = True
            elif res.action == GuardrailAction.WARNING and overall_action != GuardrailAction.BLOCK:
                overall_action = GuardrailAction.WARNING

        return results, all_violations, overall_action, not is_blocked, final_sanitized
