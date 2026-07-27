import time
from app.dto.enums import GuardrailAction, Severity
from app.dto.input import InputGuardrailRequest
from app.dto.results import GuardrailResult, GuardrailViolation
from app.interfaces.input_guardrail import InputGuardrail


class InputValidationGuardrail(InputGuardrail):
    """Guardrail to validate input completeness, payload boundaries, and attachment size limits."""

    def __init__(self, max_prompt_size_bytes: int = 102400, max_attachment_size_bytes: int = 10485760):
        self._max_prompt_size = max_prompt_size_bytes
        self._max_attachment_size = max_attachment_size_bytes

    @property
    def name(self) -> str:
        return "InputValidationGuardrail"

    async def validate(self, request: InputGuardrailRequest) -> GuardrailResult:
        start_time = time.perf_counter()
        violations: list[GuardrailViolation] = []

        # Check empty prompt
        if not request.prompt or not request.prompt.strip():
            violations.append(
                GuardrailViolation(
                    guardrail_name=self.name,
                    message="Input prompt cannot be empty or blank whitespace",
                    severity=Severity.HIGH,
                    details={"field": "prompt"},
                )
            )

        # Check max prompt size
        prompt_bytes = len(request.prompt.encode("utf-8")) if request.prompt else 0
        if prompt_bytes > self._max_prompt_size:
            violations.append(
                GuardrailViolation(
                    guardrail_name=self.name,
                    message=f"Prompt size ({prompt_bytes} bytes) exceeds max limit of {self._max_prompt_size} bytes",
                    severity=Severity.HIGH,
                    details={"prompt_bytes": prompt_bytes, "max_allowed": self._max_prompt_size},
                )
            )

        # Check attachment sizes
        for attachment in request.attachments:
            if attachment.size_bytes > self._max_attachment_size:
                violations.append(
                    GuardrailViolation(
                        guardrail_name=self.name,
                        message=f"Attachment '{attachment.filename}' size ({attachment.size_bytes} bytes) exceeds limit ({self._max_attachment_size} bytes)",
                        severity=Severity.HIGH,
                        details={"attachment": attachment.filename, "size_bytes": attachment.size_bytes},
                    )
                )

        exec_time = (time.perf_counter() - start_time) * 1000.0

        if violations:
            return GuardrailResult(
                guardrail_name=self.name,
                action=GuardrailAction.BLOCK,
                sanitized_content=None,
                score=0.0,
                violations=violations,
                execution_time_ms=exec_time,
            )

        return GuardrailResult(
            guardrail_name=self.name,
            action=GuardrailAction.ALLOW,
            sanitized_content=request.prompt,
            score=1.0,
            violations=[],
            execution_time_ms=exec_time,
        )
