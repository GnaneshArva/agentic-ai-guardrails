from typing import Optional
from app.config.settings import Settings, settings as global_settings
from app.dto.input import InputGuardrailRequest
from app.dto.output import OutputGuardrailRequest
from app.dto.results import PipelineResult
from app.factories.input_factory import InputGuardrailFactory
from app.factories.output_factory import OutputGuardrailFactory
from app.pipeline.input_pipeline import InputGuardrailPipeline
from app.pipeline.output_pipeline import OutputGuardrailPipeline


class GuardrailService:
    """Enterprise Facade service exposing simple Public API methods for Input and Output Guardrail pipelines."""

    def __init__(
        self,
        cfg: Optional[Settings] = None,
        input_pipeline: Optional[InputGuardrailPipeline] = None,
        output_pipeline: Optional[OutputGuardrailPipeline] = None,
    ):
        self._cfg = cfg or global_settings
        self._input_pipeline = input_pipeline or InputGuardrailFactory.create_pipeline(self._cfg)
        self._output_pipeline = output_pipeline or OutputGuardrailFactory.create_pipeline(self._cfg)

    @property
    def input_pipeline(self) -> InputGuardrailPipeline:
        return self._input_pipeline

    @property
    def output_pipeline(self) -> OutputGuardrailPipeline:
        return self._output_pipeline

    async def validate_input(self, request: InputGuardrailRequest) -> PipelineResult:
        """Validate request input prompt through the Input Guardrail Pipeline.

        Usage:
            result = await guardrail_service.validate_input(request)
        """
        return await self._input_pipeline.validate(request)

    async def validate_output(self, request: OutputGuardrailRequest) -> PipelineResult:
        """Validate LLM generated response through the Output Guardrail Pipeline.

        Usage:
            result = await guardrail_service.validate_output(request)
        """
        return await self._output_pipeline.validate(request)
