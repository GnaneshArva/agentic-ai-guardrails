import time
import re
from app.dto.enums import GuardrailAction, Severity
from app.dto.input import InputGuardrailRequest
from app.dto.results import GuardrailResult, GuardrailViolation
from app.interfaces.input_guardrail import InputGuardrail


class SecretDetectionGuardrail(InputGuardrail):
    """Guardrail to detect leaked secrets, API keys, AWS credentials, and private keys in prompts."""

    @property
    def name(self) -> str:
        return "SecretDetectionGuardrail"

    async def validate(self, request: InputGuardrailRequest) -> GuardrailResult:
        start_time = time.perf_counter()
        violations: list[GuardrailViolation] = []
        prompt = request.prompt

        secret_patterns = {
            "AWS Access Key": r"\b(AKIA[0-9A-Z]{16})\b",
            "GitHub Personal Access Token": r"\b(ghp_[A-Za-z0-9_]{36})\b",
            "RSA Private Key": r"-----BEGIN (RSA|OPENSSH) PRIVATE KEY-----",
            "Generic API Secret Key": r"\b(api[_-]?key|secret[_-]?key)\s*[:=]\s*['\"]?([A-Za-z0-9%_-]{16,})['\"]?\b"
        }

        detected_types: list[str] = []
        for label, pattern in secret_patterns.items():
            if re.search(pattern, prompt, re.IGNORECASE):
                detected_types.append(label)

        exec_time = (time.perf_counter() - start_time) * 1000.0

        if detected_types:
            violations.append(
                GuardrailViolation(
                    guardrail_name=self.name,
                    message=f"Prompt contains sensitive leaked credentials/secrets: {', '.join(detected_types)}.",
                    severity=Severity.CRITICAL,
                    details={"detected_secret_types": detected_types}
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

        return GuardrailResult(
            guardrail_name=self.name,
            action=GuardrailAction.ALLOW,
            sanitized_content=prompt,
            score=1.0,
            violations=[],
            execution_time_ms=exec_time,
        )
