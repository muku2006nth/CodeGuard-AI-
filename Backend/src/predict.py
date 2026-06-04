"""CodeBERT/UniXCoder inference for vulnerability classification."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

DEFAULT_MODEL = "microsoft/unixcoder-base"


@dataclass
class ClassificationResult:
    is_vulnerable: bool
    vuln_type: str
    confidence: float
    label_id: int


class VulnerabilityClassifier:
    def __init__(self, model_path: str | None = None, device: str | None = None):
        path = model_path or os.getenv(
            "MODEL_PATH",
            "models/codebert-vuln"
        )

        self.device = device or (
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        if Path(path).exists() and (Path(path) / "config.json").exists():
            print(f"Loading trained model from: {path}")

            self.tokenizer = AutoTokenizer.from_pretrained(path)
            self.model = AutoModelForSequenceClassification.from_pretrained(path)

        else:
            print("WARNING: Trained model not found.")
            print("Loading base UniXCoder model.")

            self.tokenizer = AutoTokenizer.from_pretrained(DEFAULT_MODEL)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                DEFAULT_MODEL,
                num_labels=2
            )

        self.model.to(self.device)
        self.model.eval()

        # Lower threshold works better than 0.85
        self.threshold = 0.60

    def classify(
        self,
        code: str,
        max_length: int = 512
    ) -> ClassificationResult:

        inputs = self.tokenizer(
            code,
            return_tensors="pt",
            truncation=True,
            max_length=max_length,
            padding=True,
        )

        inputs = {
            k: v.to(self.device)
            for k, v in inputs.items()
        }

        with torch.no_grad():
            outputs = self.model(**inputs)

            probs = torch.softmax(outputs.logits, dim=-1)

            print("\nRaw logits:", outputs.logits.cpu().numpy())
            print("Probabilities:", probs.cpu().numpy())

            label_id = int(probs.argmax(dim=-1).item())
            confidence = float(probs[0, label_id].item())

        is_vulnerable = (
            label_id == 1
            and confidence >= self.threshold
        )

        vuln_type = (
            "Potential Vulnerability"
            if is_vulnerable
            else "Safe"
        )
        print("Label ID:", label_id)
        print("Confidence:", confidence)
        return ClassificationResult(
            is_vulnerable=is_vulnerable,
            vuln_type=vuln_type,
            confidence=confidence,
            label_id=label_id,
        )


def predict_snippet(
    code: str,
    model_path: str | None = None
) -> ClassificationResult:

    classifier = VulnerabilityClassifier(
        model_path=model_path
    )

    return classifier.classify(code)


if __name__ == "__main__":

    sample_code = """
    import os
    cmd = input()
    os.system(cmd)
    """

    result = predict_snippet(sample_code)

    print("\\n===== RESULT =====")
    print("Vulnerable :", result.is_vulnerable)
    print("Type       :", result.vuln_type)
    print("Confidence :", round(result.confidence, 4))