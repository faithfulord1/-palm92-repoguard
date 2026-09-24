from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class MockModelAdapter:
    """Deterministic adapter for end-to-end testing without downloading a model."""

    response: str = (
        "LIKELY_FILES:\n"
        "- src/calculator.py\n\n"
        "PLAN:\n"
        "1. Inspect the failing function.\n"
        "2. Compare expected and actual behavior.\n"
        "3. Propose the smallest safe fix.\n\n"
        "RISKS:\n"
        "- Low risk: isolated application logic.\n\n"
        "NEXT_ACTIONS:\n"
        "- Read src/calculator.py\n"
        "- Run targeted tests\n"
    )

    def generate(self, *, system: str, prompt: str) -> str:
        return self.response


class TransformersGemmaAdapter:
    """Gemma 4 adapter using Hugging Face Transformers.

    Dependencies are imported lazily so RepoGuard can still run its mock
    integration tests on machines that do not have torch/transformers installed.
    """

    def __init__(
        self,
        model_id: str = "google/gemma-4-12B-it",
        *,
        max_new_tokens: int = 700,
        temperature: float = 0.2,
    ) -> None:
        self.model_id = model_id
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self._processor: Any | None = None
        self._model: Any | None = None

    def _load(self) -> None:
        if self._processor is not None and self._model is not None:
            return

        try:
            import torch
            from transformers import AutoModelForMultimodalLM, AutoProcessor
        except ImportError as exc:
            raise RuntimeError(
                "Gemma runtime dependencies are missing. "
                "Install with: pip install -e '.[gemma]'"
            ) from exc

        self._processor = AutoProcessor.from_pretrained(self.model_id)
        self._model = AutoModelForMultimodalLM.from_pretrained(
            self.model_id,
            dtype="auto",
            device_map="auto",
        )
        self._model.eval()

    def generate(self, *, system: str, prompt: str) -> str:
        self._load()
        assert self._processor is not None
        assert self._model is not None

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]

        inputs = self._processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            enable_thinking=False,
            return_dict=True,
            return_tensors="pt",
        )

        # Move tensors to the model device where possible.
        device = getattr(self._model, "device", None)
        if device is not None:
            inputs = {
                key: value.to(device) if hasattr(value, "to") else value
                for key, value in inputs.items()
            }

        outputs = self._model.generate(
            **inputs,
            max_new_tokens=self.max_new_tokens,
            do_sample=self.temperature > 0,
            temperature=max(self.temperature, 1e-5),
        )

        input_len = inputs["input_ids"].shape[-1]
        generated = outputs[0][input_len:]
        return self._processor.decode(generated, skip_special_tokens=True).strip()


@dataclass
class ScriptedModelAdapter:
    """Test adapter that returns a predefined sequence of model actions."""

    responses: list[str]
    index: int = 0

    def generate(self, *, system: str, prompt: str) -> str:
        if self.index >= len(self.responses):
            return '{"action":"final","status":"not_fixed","summary":"No scripted response left."}'
        response = self.responses[self.index]
        self.index += 1
        return response
