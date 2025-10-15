#!/usr/bin/env python3
"""
VBoarder Confidence Scorer Stub
Simple heuristic-based confidence scoring for reasoning kernel.
Replace with distilled classifier later.
"""

import re
from typing import Optional


def simple_scorer(text: str, task_context: Optional[str] = None) -> float:
    """
    Heuristic-based confidence scorer.

    Scoring factors:
    - Length (longer = more detailed)
    - Structure (lists, steps)
    - Uncertainty markers (reduce confidence)
    - Error indicators (reduce confidence)

    Args:
        text: Response text to score
        task_context: Optional task context for relevance checking

    Returns:
        float: Confidence score between 0.0 and 1.0
    """
    if not text or not text.strip():
        return 0.0

    score = 0.75  # Base confidence

    # Length factor (normalize to 200-2000 chars)
    length = len(text)
    if length < 50:
        score -= 0.3
    elif length > 200:
        score += 0.1
    if length > 500:
        score += 0.05

    # Structure indicators (lists, numbered steps)
    if re.search(r"^\d+\.", text, re.MULTILINE):
        score += 0.1  # Numbered list
    if re.search(r"^[-*]", text, re.MULTILINE):
        score += 0.05  # Bullet list

    # Uncertainty markers (penalize)
    uncertainty_patterns = [
        r"\b(maybe|perhaps|possibly|might|could be|unclear|unsure|uncertain)\b",
        r"\?\?+",  # Multiple question marks
        r"\b(I don't know|not sure|can't say)\b",
    ]
    for pattern in uncertainty_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            score -= 0.15

    # Error/problem indicators
    error_patterns = [
        r"\b(error|fail|failed|problem|issue|broken|bug)\b",
        r"\b(fix|repair|debug|troubleshoot)\b",
    ]
    for pattern in error_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            score -= 0.1

    # Positive completion indicators
    completion_patterns = [
        r"\b(complete|completed|done|finished|ready|success)\b",
        r"\b(therefore|thus|in conclusion|as a result)\b",
    ]
    for pattern in completion_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            score += 0.05

    # Clamp to [0.0, 1.0]
    return max(0.0, min(1.0, score))


def contextual_scorer(
    text: str, task: str, keywords: Optional[list] = None
) -> float:
    """
    Enhanced scorer that checks relevance to task.

    Args:
        text: Response text to score
        task: Original task/query
        keywords: Optional list of expected keywords

    Returns:
        float: Confidence score between 0.0 and 1.0
    """
    base_score = simple_scorer(text)

    # Extract keywords from task if not provided
    if keywords is None:
        # Simple keyword extraction: words longer than 4 chars
        keywords = [
            word.lower()
            for word in re.findall(r"\b\w{5,}\b", task)
            if word.lower() not in {"about", "could", "would", "should"}
        ]

    # Check keyword coverage
    if keywords:
        text_lower = text.lower()
        matched = sum(1 for kw in keywords if kw in text_lower)
        coverage = matched / len(keywords)
        base_score += coverage * 0.1

    return max(0.0, min(1.0, base_score))


# Default scorer export
def load_scorer():
    """Load default scorer function."""
    return simple_scorer


if __name__ == "__main__":
    # Test scorer
    test_cases = [
        ("Yes", 0.5),  # Too short
        ("I don't know, maybe it could work?", 0.4),  # Uncertain
        (
            "Here are the steps:\n1. First do X\n2. Then do Y\n3. Complete Z\nTherefore, the task is done.",
            0.9,
        ),
        ("Error: failed to process", 0.3),
    ]

    print("🧪 Testing scorer:")
    for text, expected in test_cases:
        score = simple_scorer(text)
        print(f"  Text: {text[:50]}...")
        print(f"  Score: {score:.2f} (expected ~{expected})")
        print()
