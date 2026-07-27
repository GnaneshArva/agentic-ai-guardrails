import json
import time
from typing import Any, Optional, Type
from pydantic import BaseModel, ValidationError
from app.dto.enums import GuardrailAction, Severity
from app.dto.output import OutputGuardrailRequest
from app.dto.results import GuardrailResult, GuardrailViolation
from app.interfaces.output_guardrail import OutputGuardrail


class StructuredOutputGuardrail(OutputGuardrail):
    """Guardrail to validate LLM responses against a target Pydantic model or JSON Schema."""

    def __init__(self, target_model: Optional[Type[BaseModel]] = None):
        self._target_model = target_model

    @property
    def name(self) -> str:
        return "StructuredOutputGuardrail"

    async def validate(self, request: OutputGuardrailRequest) -> GuardrailResult:
        start_time = time.perf_counter()
        violations: list[GuardrailViolation] = []

        # Target schema can come from constructor or request DTO
        if not self._target_model and not request.target_schema:
            exec_time = (time.perf_counter() - start_time) * 1000.0
            return GuardrailResult(
                guardrail_name=self.name,
                action=GuardrailAction.ALLOW,
                sanitized_content=request.response_text,
                score=1.0,
                violations=[],
                execution_time_ms=exec_time,
            )

        # Parse JSON output
        try:
            parsed_json = json.loads(request.response_text)
        except json.JSONDecodeError as err:
            exec_time = (time.perf_counter() - start_time) * 1000.0
            violations.append(
                GuardrailViolation(
                    guardrail_name=self.name,
                    message=f"Output is not valid JSON: {str(err)}",
                    severity=Severity.HIGH,
                    details={"error": str(err)},
                )
            )
            return GuardrailResult(
                guardrail_name=self.name,
                action=GuardrailAction.BLOCK,
                sanitized_content=None,
                score=0.0,
                violations=violations,
                execution_time_ms=exec_time,
            )

        # Validate with Pydantic model if provided
        if self._target_model:
            try:
                validated_obj = self._target_model.model_validate(parsed_json)
                exec_time = (time.perf_counter() - start_time) * 1000.0
                return GuardrailResult(
                    guardrail_name=self.name,
                    action=GuardrailAction.ALLOW,
                    sanitized_content=validated_obj.model_dump(),
                    score=1.0,
                    violations=[],
                    execution_time_ms=exec_time,
                )
            except ValidationError as val_err:
                for err in val_err.errors():
                    loc_str = "->".join([str(x) for x in err["loc"]])
                    violations.append(
                        GuardrailViolation(
                            guardrail_name=self.name,
                            message=f"Schema validation error at '{loc_str}': {err['msg']}",
                            severity=Severity.HIGH,
                            details=err,
                        )
                    )

        # Validate required fields if raw json schema dict provided in request
        if request.target_schema and isinstance(request.target_schema, dict):
            required_fields = request.target_schema.get("required", [])
            for field in required_fields:
                if field not in parsed_json:
                    violations.append(
                        GuardrailViolation(
                            guardrail_name=self.name,
                            message=f"Missing required schema field: '{field}'",
                            severity=Severity.HIGH,
                            details={"missing_field": field},
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
            sanitized_content=parsed_json,
            score=1.0,
            violations=[],
            execution_time_ms=exec_time,
        )
