# Step-by-Step Execution Architecture (`agentic-ai-guardrails`)

## Purpose
`agentic-ai-guardrails` is a standalone, enterprise-grade Python security and compliance microservice. It provides independent **Input** and **Output** validation pipelines to enforce prompt safety, PII data privacy, RAG grounding, citation verification, and domain policy compliance.

---

## Step-by-Step Request Execution Flow

### 1. Input Guardrail Pipeline (`POST /guardrails/input/validate`)

```
Client Prompt ──► [1. Validation] ──► [2. Prompt Injection] ──► [3. Jailbreak] ──► [4. PII Masking] ──► [5. Business Rules] ──► Sanitized Request / LLM
```

1. **Request Ingestion**: Receives `InputGuardrailRequest` payload (`prompt`, `user_id`, `session_id`, `attachments`).
2. **`InputValidationGuardrail`**: Validates basic payload boundaries (non-empty prompt, size limits).
3. **`PromptInjectionGuardrail`**: Scans prompt text against regular expression rules for injection attacks (e.g., `"ignore previous instructions"`). Halts immediately if triggered when `STOP_ON_FIRST_FAILURE=True`.
4. **`JailbreakGuardrail`**: Detects DAN / persona override attempts.
5. **`PiiInputGuardrail`**: Identifies sensitive personal data (email, phone, SSN, credit cards). Applies policy (`MASK`, `REJECT`, or `WARN`). If `MASK`, passes sanitized prompt forward.
6. **`BusinessValidationGuardrail`**: Executes domain-specific rules.
7. **Result Assembly**: Returns `PipelineResult` containing `is_allowed`, `sanitized_request`, and violation details.

---

### 2. Output Guardrail Pipeline (`POST /guardrails/output/validate`)

```
LLM Response ──► [1. Toxicity] ──► [2. Hallucination] ──► [3. Citations] ──► [4. PII Redaction] ──► [5. Schema Check] ──► Safe User Output
```

1. **Response Ingestion**: Receives `OutputGuardrailRequest` payload (`response_text`, `retrieved_context`, `target_schema`).
2. **`ToxicityGuardrail`**: Evaluates response text for abusive, toxic, or unsafe language against configured thresholds.
3. **`HallucinationGuardrail`**: Compares response against `retrieved_context` (RAG passages) to calculate grounding scores (requires minimum score, e.g. 0.60).
4. **`CitationGuardrail`**: Verifies that references cited in the output match actual retrieved source IDs.
5. **`PiiOutputGuardrail`**: Redacts leaked sensitive data or secrets from model output before user delivery.
6. **`StructuredOutputGuardrail`**: Validates JSON response structure against `target_schema` if specified.
7. **`BusinessOutputGuardrail`**: Validates domain response constraints (e.g., blocking unverified refund promises).
8. **Result Assembly**: Returns `PipelineResult` containing `is_allowed`, `sanitized_response`, and violation details.
