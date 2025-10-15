#!/usr/bin/env python3
"""
VBoarder Reasoning Kernel - Multi-step reasoning with confidence scoring
Enables agents to loop through tasks with dynamic model switching.
"""

import logging
from dataclasses import dataclass
from typing import Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class LoopCfg:
    """Configuration for reasoning loop"""

    max_iterations: int = 5
    confidence_threshold: float = 0.85
    min_confidence: float = 0.5
    escalate_on_low_confidence: bool = True


class ReasoningKernel:
    """
    Lightweight reasoning kernel for multi-step task processing.

    Features:
    - Confidence-based iteration
    - Dynamic model slot selection
    - Early stopping on high confidence
    - Escalation on low confidence
    """

    def __init__(
        self,
        model: Callable,
        scorer: Callable[[str], float],
        config: Optional[LoopCfg] = None,
    ):
        """
        Initialize reasoning kernel.

        Args:
            model: Callable that takes (prompt: str) -> str
            scorer: Callable that takes (text: str) -> float (0.0-1.0)
            config: Optional LoopCfg for tuning behavior
        """
        self.model = model
        self.scorer = scorer
        self.config = config or LoopCfg()

    def answer(self, task: str, context: Optional[str] = None) -> dict:
        """
        Process task through reasoning loop.

        Args:
            task: User's query or task description
            context: Optional context from previous interactions

        Returns:
            dict with:
                - result: final answer text
                - iterations: number of loops performed
                - confidence: final confidence score
                - reasoning_chain: list of intermediate steps
        """
        reasoning_chain = []
        current_prompt = self._build_initial_prompt(task, context)

        for iteration in range(self.config.max_iterations):
            # Generate response
            response = self.model(current_prompt)

            # Score confidence
            confidence = self.scorer(response)

            # Log step
            step = {
                "iteration": iteration + 1,
                "response": response,
                "confidence": confidence,
            }
            reasoning_chain.append(step)

            logger.info(
                f"Iteration {iteration + 1}: confidence={confidence:.2f}"
            )

            # Early exit on high confidence
            if confidence >= self.config.confidence_threshold:
                logger.info("High confidence achieved, stopping early")
                return {
                    "result": response,
                    "iterations": iteration + 1,
                    "confidence": confidence,
                    "reasoning_chain": reasoning_chain,
                    "status": "success",
                }

            # Check for low confidence
            if confidence < self.config.min_confidence:
                if self.config.escalate_on_low_confidence:
                    logger.warning(
                        f"Low confidence ({confidence:.2f}), escalating"
                    )
                    return {
                        "result": response,
                        "iterations": iteration + 1,
                        "confidence": confidence,
                        "reasoning_chain": reasoning_chain,
                        "status": "escalate",
                        "reason": "confidence_too_low",
                    }

            # Refine prompt for next iteration
            current_prompt = self._refine_prompt(task, response, confidence)

        # Max iterations reached
        final_response = reasoning_chain[-1]["response"]
        final_confidence = reasoning_chain[-1]["confidence"]

        return {
            "result": final_response,
            "iterations": self.config.max_iterations,
            "confidence": final_confidence,
            "reasoning_chain": reasoning_chain,
            "status": "max_iterations_reached",
        }

    def _build_initial_prompt(self, task: str, context: Optional[str]) -> str:
        """Build initial prompt for task."""
        if context:
            return f"Context: {context}\n\nTask: {task}\n\nProvide a detailed, step-by-step answer."
        return f"Task: {task}\n\nProvide a detailed, step-by-step answer."

    def _refine_prompt(
        self, original_task: str, previous_response: str, confidence: float
    ) -> str:
        """Refine prompt based on previous iteration."""
        return f"""Original task: {original_task}

Previous attempt: {previous_response}

This response had confidence of {confidence:.2f}. Please refine your answer:
- Address any unclear points
- Add more specific details
- Verify logical consistency
"""


# Factory function for easy instantiation
def create_reasoning_kernel(
    model_loader: Callable,
    scorer_loader: Callable,
    max_iterations: int = 5,
    confidence_threshold: float = 0.85,
) -> ReasoningKernel:
    """
    Factory to create a reasoning kernel with default settings.

    Args:
        model_loader: Function that returns a model callable
        scorer_loader: Function that returns a scorer callable
        max_iterations: Max reasoning loop iterations
        confidence_threshold: Confidence threshold for early stopping

    Returns:
        Configured ReasoningKernel instance
    """
    model = model_loader()
    scorer = scorer_loader()
    config = LoopCfg(
        max_iterations=max_iterations,
        confidence_threshold=confidence_threshold,
    )
    return ReasoningKernel(model, scorer, config)
