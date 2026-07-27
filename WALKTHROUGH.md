# Walkthrough - Enterprise Agentic AI Guardrails (`agentic-ai-guardrails`)

The enterprise-grade Guardrails Framework **`agentic-ai-guardrails`** has been implemented, validated, and verified.

## Accomplished Features

### 1. Architecture & Design Patterns
- **Clean Architecture & SOLID**: Clean decoupling of strategies, DTOs, factories, pipelines, and facade services.
- **Strategy Pattern**: Extensible strategy base classes [InputGuardrail](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/interfaces/input_guardrail.py) and [OutputGuardrail](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/interfaces/output_guardrail.py).
- **Chain of Responsibility Pattern**: Sequential execution engine with configurable early stopping (`STOP_ON_FIRST_FAILURE=True`) in [base_pipeline.py](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/pipeline/base_pipeline.py).
- **Parallel Execution Mode**: High-throughput concurrent execution using `asyncio.gather`.
- **Factory Pattern**: [InputGuardrailFactory](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/factories/input_factory.py) and [OutputGuardrailFactory](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/factories/output_factory.py).
- **Facade Service**: High-level public API [GuardrailService](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/services/guardrail_service.py).
- **Pydantic v2 DTOs**: Strict type safety across all requests, responses, results, and violations in [app/dto/](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/dto).

### 2. Input Guardrails Pipeline
1. `PromptInjectionGuardrail`: Detects prompt overrides, system prompt leaks, and developer instruction bypasses.
2. `JailbreakGuardrail`: Detects DAN (Do Anything Now), Developer Mode, and persona bypasses.
3. `PiiInputGuardrail`: Detects and handles (MASK / REJECT / WARN) Credit Cards, Passport, Aadhaar, PAN, SSN, API Keys, and Passwords.
4. `InputValidationGuardrail`: Enforces non-empty prompts, length limits, and attachment sizes.
5. `BusinessValidationGuardrail`: Enforces pluggable domain rules (e.g. Travel Agent rejecting unauthorized HR/payroll access).

### 3. Output Guardrails Pipeline
1. `PiiOutputGuardrail`: Redacts credit cards, passports, emails, phone numbers, and secrets in LLM responses.
2. `ToxicityGuardrail`: Detects hate speech, harassment, abuse, and offensive language.
3. `HallucinationGuardrail`: Grounding verification comparing output against retrieved RAG context.
4. `CitationGuardrail`: Verifies cited doc IDs exist within valid source contexts.
5. `StructuredOutputGuardrail`: Validates response against Pydantic model or JSON schema.
6. `BusinessOutputGuardrail`: Enforces domain business rules (e.g. verifying refund approvals match tool call records).

---

## Verification Results

### 1. Pytest Unit Test Suite
Ran `pytest tests/ -v`:
- **14 passed in 0.09 seconds**

```
tests/test_guardrails.py::test_prompt_injection_guardrail_block PASSED   [  7%]
tests/test_guardrails.py::test_jailbreak_guardrail_block PASSED          [ 14%]
tests/test_guardrails.py::test_pii_input_guardrail_mask PASSED           [ 21%]
tests/test_guardrails.py::test_input_validation_guardrail_empty_prompt PASSED [ 28%]
tests/test_guardrails.py::test_business_input_validation_guardrail PASSED [ 35%]
tests/test_guardrails.py::test_pii_output_guardrail_mask PASSED          [ 42%]
tests/test_guardrails.py::test_toxicity_guardrail_block PASSED           [ 50%]
tests/test_guardrails.py::test_hallucination_guardrail PASSED            [ 57%]
tests/test_guardrails.py::test_citation_guardrail_fabricated PASSED      [ 64%]
tests/test_guardrails.py::test_structured_output_guardrail_valid PASSED  [ 71%]
tests/test_guardrails.py::test_business_output_guardrail_unverified_refund PASSED [ 78%]
tests/test_guardrails.py::test_pipeline_sequential_early_stop PASSED     [ 85%]
tests/test_guardrails.py::test_pipeline_parallel_mode PASSED             [ 92%]
tests/test_guardrails.py::test_guardrail_service_end_to_end PASSED       [100%]
```

### 2. Demonstration Run (`demo.py`)
Ran `python3 demo.py` showcasing all 7 core scenarios:
- Safe input validation
- Malicious input detection (Prompt Injection & PII)
- PII masking on input prompt
- Safe LLM output validation
- Unsafe LLM output detection (Toxicity & Secrets)
- Parallel execution mode across 5 concurrent guardrails
- Custom guardrail extension (`CustomSqlInjectionGuardrail`)

---

## Documentation & Integration Guides
Comprehensive enterprise [README.md](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/README.md) includes:
- Architecture principles & diagrams
- Comparison table of Input vs Output Guardrails
- Sequential (Chain of Responsibility) & Parallel execution mode details
- Step-by-step custom guardrail extension guide
- Complete code examples for Model Context Protocol (MCP) Server integration
- Complete code examples for OpenAI Agents SDK integration
