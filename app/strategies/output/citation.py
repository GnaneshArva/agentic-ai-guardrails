import time
import re
from app.dto.enums import GuardrailAction, Severity
from app.dto.output import OutputGuardrailRequest
from app.dto.results import GuardrailResult, GuardrailViolation
from app.interfaces.output_guardrail import OutputGuardrail


class CitationGuardrail(OutputGuardrail):
    """Guardrail to verify all cited sources exist in the retrieved context IDs."""

    @property
    def name(self) -> str:
        return "CitationGuardrail"

    async def validate(self, request: OutputGuardrailRequest) -> GuardrailResult:
        start_time = time.perf_counter()
        violations: list[GuardrailViolation] = []

        # Find citation markers in response, e.g. [doc-123], [ref:XYZ], [source-1]
        cited_in_text = set(re.findall(r"\[((?:doc|source|ref)[:\s-]?[a-zA-Z0-9_-]+)\]", request.response_text, re.IGNORECASE))
        # Add citations explicitly provided in DTO
        all_cited_sources = cited_in_text.union(set(request.citations))

        valid_sources = set(request.metadata.get("valid_source_ids", []))
        # If retrieved context strings contain doc IDs in metadata or text, include them
        for context_item in request.retrieved_context:
            found_ids = re.findall(r"\[((?:doc|source|ref)[:\s-]?[a-zA-Z0-9_-]+)\]", context_item, re.IGNORECASE)
            valid_sources.update(found_ids)

        # If valid_sources list is empty, we infer citations cannot be verified against zero sources if citations exist
        invalid_citations = []
        if all_cited_sources and valid_sources:
            invalid_citations = [c for c in all_cited_sources if c not in valid_sources]

        for invalid_cite in invalid_citations:
            violations.append(
                GuardrailViolation(
                    guardrail_name=self.name,
                    message=f"Fabricated or invalid source citation detected: '{invalid_cite}'",
                    severity=Severity.HIGH,
                    details={"citation": invalid_cite, "valid_sources": list(valid_sources)},
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
            sanitized_content=request.response_text,
            score=1.0,
            violations=[],
            execution_time_ms=exec_time,
        )
