import re
from typing import Pattern

# PII Patterns
CREDIT_CARD_PATTERN: Pattern[str] = re.compile(
    r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|(?:2131|1800|35\d{3})\d{11})\b"
)
SSN_PATTERN: Pattern[str] = re.compile(
    r"\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b"
)
AADHAAR_PATTERN: Pattern[str] = re.compile(
    r"\b[2-9]{1}\d{3}\s?\d{4}\s?\d{4}\b"
)
PAN_PATTERN: Pattern[str] = re.compile(
    r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"
)
PASSPORT_PATTERN: Pattern[str] = re.compile(
    r"\b[A-PR-WYa-pr-wy][1-9]\d{7}\b"
)
API_KEY_PATTERN: Pattern[str] = re.compile(
    r"(?i)\b(?:sk-[a-zA-Z0-9]{20,T?|api[_-]?key[_-]?[a-zA-Z0-9_-]{16,}|bearer\s+[a-zA-Z0-9\-\._~\+\/]+=*|AKIA[0-9A-Z]{16})\b"
)
PASSWORD_PATTERN: Pattern[str] = re.compile(
    r"(?i)\b(?:password|passwd|secret)\s*[:=]\s*['\"]?([^\s'\"]{4,})['\"]?"
)
EMAIL_PATTERN: Pattern[str] = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)
PHONE_PATTERN: Pattern[str] = re.compile(
    r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
)

# Prompt Injection Patterns
PROMPT_INJECTION_PATTERNS: list[Pattern[str]] = [
    re.compile(r"(?i)ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|directives|rules|prompts)"),
    re.compile(r"(?i)reveal\s+(your\s+)?(system\s+prompt|developer\s+instructions|initial\s+prompt)"),
    re.compile(r"(?i)override\s+(developer|system|safety)\s+(instructions|guidelines|controls)"),
    re.compile(r"(?i)print\s+(the\s+)?system\s+prompt"),
    re.compile(r"(?i)disregard\s+all\s+(prior|previous)\s+safety"),
    re.compile(r"(?i)what\s+is\s+your\s+system\s+prompt"),
]

# Jailbreak Patterns
JAILBREAK_PATTERNS: list[Pattern[str]] = [
    re.compile(r"(?i)\bDAN\b|\bDo\s+Anything\s+Now\b"),
    re.compile(r"(?i)developer\s+mode\s+(enabled|on|active)"),
    re.compile(r"(?i)ignore\s+(all\s+)?restrictions"),
    re.compile(r"(?i)stay\s+in\s+character\s+as"),
    re.compile(r"(?i)jailbreak\s+mode"),
    re.compile(r"(?i)unfiltered\s+and\s+unrestricted"),
    re.compile(r"(?i)simulate\s+an\s+evil\s+AI"),
]

# Toxicity Keywords / Patterns
TOXICITY_PATTERNS: list[Pattern[str]] = [
    re.compile(r"(?i)\b(hate\s+speech|kill\s+yourself|die|slur|abuse|harass|idiot|stupid|scam|fraud)\b"),
    re.compile(r"(?i)\b(offensive\s+language|violent\s+threat)\b"),
]
