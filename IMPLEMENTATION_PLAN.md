# Enterprise Agentic AI Guardrails Framework (agentic-ai-guardrails)

Build an Enterprise-grade Guardrails Framework named `agentic-ai-guardrails`. The framework provides reusable, standalone Input and Output Guardrail pipelines that plug into any Agentic AI application, MCP Server, AI Gateway, or AI Orchestrator without binding to a specific LLM or domain.

## Architecture & Design Patterns

1. **Clean Architecture & SOLID Principles**: Strictly decoupled domain logic, pipeline abstractions, strategies, DTOs, and configuration.
2. **Strategy Pattern**: Abstract base classes `InputGuardrail` and `OutputGuardrail` defining the `async validate(...)` contract.
3. **Chain of Responsibility Pattern**: Pipeline executes guardrails in order. Sequential mode halts execution immediately upon a blocking violation when `stop_on_first_failure=True` and returns a structured failure `PipelineResult`.
4. **Parallel Mode**: Concurrently runs independent guardrails via `asyncio.gather` and consolidates results.
5. **Factory Pattern**: `InputGuardrailFactory` and `OutputGuardrailFactory` construct pre-configured pipelines dynamically based on configuration.
6. **Dependency Injection**: Guardrails and pipelines accept dependencies (settings, rules, validators) explicitly.
7. **Pydantic v2 DTOs**: Strict type safety with zero raw dictionaries in request/response payloads.

---

## Proposed Changes

### Configuration & Setup

#### [NEW] [pyproject.toml](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/pyproject.toml)
- Modern `pyproject.toml` supporting Python 3.12+, `pydantic>=2.0`, `pydantic-settings`, and development/testing tools (`pytest`, `pytest-asyncio`). Compatible with `uv` package manager.

#### [NEW] [.env.example](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/.env.example)
- Configuration template with feature flags (`ENABLE_PROMPT_INJECTION`, `ENABLE_JAILBREAK`, `ENABLE_PII`, `ENABLE_TOXICITY`, `ENABLE_HALLUCINATION`, `ENABLE_CITATION`, `ENABLE_OUTPUT_VALIDATION`, `ENABLE_BUSINESS_INPUT`, `ENABLE_BUSINESS_OUTPUT`), pipeline options (`EXECUTION_MODE`, `STOP_ON_FIRST_FAILURE`), and threshold limits.

---

### Core Application (`app/`)

#### [NEW] [app/config/settings.py](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/config/settings.py)
- Pydantic Settings class loading environment variables for guardrail toggles, mode selections (Sequential vs Parallel), PII action policies (MASK, REJECT, WARN), max prompt size (e.g. 100KB), max attachment size (e.g. 10MB), and custom threshold scores.

#### [NEW] [app/dto/enums.py](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/dto/enums.py)
- Enums: `GuardrailAction` (ALLOW, BLOCK, WARNING), `ExecutionMode` (SEQUENTIAL, PARALLEL), `Severity` (LOW, MEDIUM, HIGH, CRITICAL), `PiiAction` (MASK, REJECT, WARN).

#### [NEW] [app/dto/input.py](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/dto/input.py)
- `InputGuardrailRequest`: prompt, user_id, session_id, metadata, attachments (list of metadata), system_prompt (optional), custom_rules.

#### [NEW] [app/dto/output.py](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/dto/output.py)
- `OutputGuardrailRequest`: response_text, retrieved_context (list of doc strings/dicts), target_schema (Pydantic model/JSON schema), citations (list of source IDs), tool_calls (list of tool executions/results), metadata.

#### [NEW] [app/dto/results.py](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/dto/results.py)
- `GuardrailViolation`: guardrail_name, message, severity, details.
- `GuardrailResult`: guardrail_name, action, sanitized_content, score, violations, execution_time_ms.
- `PipelineResult`: is_allowed, action, violations, sanitized_request / sanitized_response, total_execution_time_ms, guardrail_results.

#### [NEW] [app/interfaces/input_guardrail.py](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/interfaces/input_guardrail.py)
- `InputGuardrail(ABC)` interface with abstract method `async validate(self, request: InputGuardrailRequest) -> GuardrailResult`.

#### [NEW] [app/interfaces/output_guardrail.py](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/interfaces/output_guardrail.py)
- `OutputGuardrail(ABC)` interface with abstract method `async validate(self, request: OutputGuardrailRequest) -> GuardrailResult`.

#### [NEW] [app/utils/regex_patterns.py](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/utils/regex_patterns.py)
- Pattern definitions for PII (Credit Cards, Passport, Aadhaar, PAN, SSN, API Keys, Passwords, Emails, Phone numbers), Prompt Injection phrases, Jailbreak markers (DAN, Developer Mode), and Toxicity terms.

#### [NEW] [app/exceptions/guardrail_exceptions.py](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/exceptions/guardrail_exceptions.py)
- Custom exceptions: `GuardrailException`, `GuardrailConfigurationError`, `GuardrailPipelineError`.

---

### Guardrail Strategies (`app/strategies/`)

#### Input Guardrails (`app/strategies/input/`)
- [NEW] `prompt_injection.py`: Detects system prompt overrides, prompt leakage, "ignore instructions".
- [NEW] `jailbreak.py`: Detects DAN, Developer Mode, role-play bypass attempts.
- [NEW] `pii_input.py`: Detects & handles (MASK / REJECT / WARN) Sensitive information (Credit Card, Aadhaar, PAN, SSN, API Keys, Passwords).
- [NEW] `input_validation.py`: Validates non-empty prompt, prompt length limits, attachment size limits.
- [NEW] `business_input_validation.py`: Pluggable enterprise domain rules (e.g. Travel Agent rejecting unauthorized actions like "delete payroll", "access HR database").

#### Output Guardrails (`app/strategies/output/`)
- [NEW] `pii_output.py`: Redacts/masks PII details (credit cards, passports, emails, phones, secrets) in LLM responses.
- [NEW] `toxicity.py`: Detects hate speech, harassment, abuse, and offensive language.
- [NEW] `hallucination.py`: Grounding check comparing generated statements against provided retrieval context.
- [NEW] `citation.py`: Verifies all citations and source IDs against valid retrieved context documents.
- [NEW] `structured_output.py`: Validates output format against Pydantic schema or JSON schema.
- [NEW] `business_output_validation.py`: Enforces business invariants (e.g. verifying refund approvals against tool execution status).

---

### Pipelines & Factories (`app/pipeline/`, `app/factories/`, `app/services/`)

#### [NEW] [app/pipeline/input_pipeline.py](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/pipeline/input_pipeline.py)
- `InputGuardrailPipeline` implementing Chain of Responsibility (Sequential with optional early-stop) and Parallel (`asyncio.gather`) modes.

#### [NEW] [app/pipeline/output_pipeline.py](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/pipeline/output_pipeline.py)
- `OutputGuardrailPipeline` implementing Chain of Responsibility (Sequential with optional early-stop) and Parallel modes.

#### [NEW] [app/factories/input_factory.py](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/factories/input_factory.py)
- `InputGuardrailFactory` creating configured input pipelines.

#### [NEW] [app/factories/output_factory.py](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/factories/output_factory.py)
- `OutputGuardrailFactory` creating configured output pipelines.

#### [NEW] [app/services/guardrail_service.py](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/app/services/guardrail_service.py)
- High-level Facade service for simple API integration (`validate_input` & `validate_output`).

---

### Documentation, Integration Examples & Demonstration

#### [MODIFY] [README.md](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/README.md)
- Complete, exhaustive README documentation matching all required sections (Overview, Architecture, Input vs Output, Design Patterns, Execution Modes, Configuration, Extension Guide, MCP Server Integration, OpenAI Agents SDK Integration, Request Lifecycle, Failure Examples, Best Practices).

#### [NEW] [demo.py](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/demo.py)
- Runnable demo showcasing successful passes, prompt injection blocks, PII masking, toxicity detection, citation validation, structured output validation, sequential vs parallel execution, and custom guardrail extension.

#### [NEW] [tests/test_guardrails.py](file:///Users/gnanesh_arva/Downloads/travel-planner-v2/agentic-ai-guardrails/tests/test_guardrails.py)
- Comprehensive `pytest` test suite covering unit tests for all input and output guardrails, pipeline modes, and factory initialization.

---

## Verification Plan

### Automated Tests
1. Environment & Dependency Setup:
   - Create Python venv and install required dependencies (`pydantic`, `pytest`, `pytest-asyncio`).
2. Run pytest suite:
   - `pytest tests/ -v`
3. Execute `demo.py`:
   - `python3 demo.py` and verify zero errors, checking correct ALLOW / BLOCK / WARNING outputs.

### Manual Verification
- Review generated `README.md` to ensure all architectural principles and integration code snippets (MCP Server, OpenAI SDK) are fully documented.
