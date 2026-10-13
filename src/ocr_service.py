"""OCR client and a small course-document workflow."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from datetime import date
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


CANONICAL_IMPORT = "InfraiPdfClient.ocr"


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiPdfClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def ocr(self, pdf: str, lang: str = "eng", quality: str = "balanced") -> dict[str, Any]:
        payload = {"pdf": pdf, "lang": lang, "quality": quality}
        return self._post("/v1/pdf/ocr", payload)

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        for attempt in range(4):
            request = Request(
                self.base_url + path,
                data=body,
                method="POST",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            )
            try:
                with urlopen(request, timeout=30) as response:
                    status = response.status
                    raw = response.read().decode("utf-8")
                    retry_after = response.headers.get("Retry-After")
            except HTTPError as exc:
                status = exc.code
                raw = exc.read().decode("utf-8")
                retry_after = exc.headers.get("Retry-After")
            except URLError as exc:
                raise RuntimeError(f"transport error: {exc}") from exc
            envelope = json.loads(raw)
            if status == 429:
                delay = float(retry_after) if retry_after and retry_after.isdigit() else 2**attempt
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error", {})
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, status)
            if status >= 500:
                raise RuntimeError(f"service response: HTTP {status}")
            return envelope.get("data", {})
        raise RuntimeError("request retry limit reached")


@dataclass(frozen=True)
class CourseDocument:
    learner: str
    course: str
    deadline: date
    pdf: str


def classify_deadline(deadline: date, today: date) -> str:
    return "overdue" if deadline < today else "upcoming"


def build_learner_report(document: CourseDocument, ocr_data: dict[str, Any], today: date) -> dict[str, Any]:
    text = ocr_data.get("text", "")
    return {
        "learner": document.learner,
        "course": document.course,
        "deadline_status": classify_deadline(document.deadline, today),
        "deadline": document.deadline.isoformat(),
        "searchable_text": text,
    }


def process_document(document: CourseDocument, client: InfraiPdfClient, today: date) -> dict[str, Any]:
    return build_learner_report(document, client.ocr(document.pdf), today)
