import time
import re
from typing import List
from app.dto.enums import GuardrailAction, Severity
from app.dto.output import OutputGuardrailRequest
from app.dto.results import GuardrailResult, GuardrailViolation
from app.interfaces.output_guardrail import OutputGuardrail


class CoherenceGuardrail(OutputGuardrail):
    """Guardrail to verify logical response flow, day-by-day continuity, and structural consistency.
    
    Evaluates:
    - Day-by-day itinerary sequence continuity (e.g. Day 1, Day 2, Day 3 without gaps or out-of-order jumps).
    - Paragraph transition smoothness and non-contradiction heuristics.
    - Formatting structure & section logical cohesion.
    """

    def __init__(self, min_coherence_score: float = 0.70):
        self._min_coherence_score = min_coherence_score

    @property
    def name(self) -> str:
        return "CoherenceGuardrail"

    async def validate(self, request: OutputGuardrailRequest) -> GuardrailResult:
        start_time = time.perf_counter()
        violations: List[GuardrailViolation] = []
        text = request.response_text.strip()

        if not text:
            exec_time = (time.perf_counter() - start_time) * 1000.0
            return GuardrailResult(
                guardrail_name=self.name,
                action=GuardrailAction.BLOCK,
                sanitized_content=None,
                score=0.0,
                violations=[
                    GuardrailViolation(
                        guardrail_name=self.name,
                        message="Response text is empty. Zero coherence.",
                        severity=Severity.HIGH,
                        details={"coherence_score": 0.0}
                    )
                ],
                execution_time_ms=exec_time,
            )

        # 1. Day-by-Day Sequence Continuity Check
        day_matches = [int(m) for m in re.findall(r"(?:Day|day)\s*(\d+)", text)]
        sequence_score = 1.0
        sequence_issues: List[str] = []

        if day_matches:
            # Verify days start logically and proceed in monotonic ascending sequence
            for i in range(1, len(day_matches)):
                prev_day = day_matches[i - 1]
                curr_day = day_matches[i]
                if curr_day < prev_day:
                    sequence_issues.append(f"Out-of-order timeline jump: Day {curr_day} appears after Day {prev_day}.")
                elif curr_day > prev_day + 2:
                    sequence_issues.append(f"Timeline gap detected: Jumped from Day {prev_day} directly to Day {curr_day}.")

            if sequence_issues:
                sequence_score = max(0.20, 1.0 - (len(sequence_issues) * 0.30))

        # 2. Structural & Transition Cohesion Check
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        structure_score = 1.0
        if len(paragraphs) == 1 and len(text.split()) > 150:
            # Overly monolithic paragraph without section breaks
            structure_score = 0.70

        # 3. Contradiction & Location Jump Heuristic
        location_mentions = re.findall(r"\b(?:Tokyo|Paris|Rome|London|New York|Zurich|Bern|Lucerne|Interlaken|Geneva|Swiss)\b", text, re.IGNORECASE)
        contradiction_issues: List[str] = []
        
        # Check if single short day itinerary mentions widely conflicting distant countries simultaneously without transit
        if len(set([loc.lower() for loc in location_mentions])) > 3 and "day 1" in text.lower() and "day 2" not in text.lower():
            contradiction_issues.append("Multiple distant destination cities mentioned without clear multi-day travel sequence.")

        contradiction_score = 0.50 if contradiction_issues else 1.0

        # Weighted final coherence score calculation
        coherence_score = (sequence_score * 0.50) + (structure_score * 0.30) + (contradiction_score * 0.20)
        coherence_score = round(max(0.0, min(1.0, coherence_score)), 2)

        exec_time = (time.perf_counter() - start_time) * 1000.0

        if coherence_score < self._min_coherence_score or sequence_issues or contradiction_issues:
            all_messages = sequence_issues + contradiction_issues
            msg = "; ".join(all_messages) if all_messages else f"Low coherence score ({coherence_score:.2f} < {self._min_coherence_score:.2f})."
            
            violations.append(
                GuardrailViolation(
                    guardrail_name=self.name,
                    message=f"Coherence violation: {msg}",
                    severity=Severity.HIGH,
                    details={
                        "coherence_score": coherence_score,
                        "min_required": self._min_coherence_score,
                        "sequence_issues": sequence_issues,
                        "contradiction_issues": contradiction_issues,
                        "remediation_instruction": "Rewrite the response to enforce clear logical section flow and sequential day-by-day continuity without changing retrieved facts, flight options, or hotel prices."
                    },
                )
            )
            return GuardrailResult(
                guardrail_name=self.name,
                action=GuardrailAction.BLOCK if coherence_score < 0.50 else GuardrailAction.WARNING,
                sanitized_content=None if coherence_score < 0.50 else request.response_text,
                score=coherence_score,
                violations=violations,
                execution_time_ms=exec_time,
            )

        return GuardrailResult(
            guardrail_name=self.name,
            action=GuardrailAction.ALLOW,
            sanitized_content=request.response_text,
            score=coherence_score,
            violations=[],
            execution_time_ms=exec_time,
        )
