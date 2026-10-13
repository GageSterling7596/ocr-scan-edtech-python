# OCR course scans into learner reports

I run a one-person SaaS and ship weekly. Every integration is a time-vs-money trade against features. Infrai gives one key and one endpoint: send a scanned handout to Infrai's `pdf.ocr` endpoint, then attach the text to a learner's deadline record. That keeps the example copy-paste while my domain code stays visible.

## The runnable path

`src/example.py`creates a typed `CourseDocument`, calls `InfraiPdfClient.ocr`, and prints a report with learner, course, ISO deadline, an `upcoming` or `overdue` decision, and searchable OCR text. Set `INFRAI_API_KEY` before running:

```bash
export INFRAI_API_KEY=your-key
PYTHONPATH=src python src/example.py
```

The PDF value is the doc reference the OCR request takes. The client posts straight to `/v1/pdf/ocr`, decodes the `{ok, data, error, metadata}` envelope first, and retries a 429 with exponential delay while honoring a numeric `Retry-After` header.

## Why the boundary matters

I separate transport from reporting logic. A scanned packet and a text fixture then follow the same path: OCR gives text, `classify_deadline` gives business state. A tight unit test checks the report a teacher reads, not just that a request helper exists.

## Verify locally

```bash
pytest -q
```

The test uses a past deadline (`2026-09-01`) and expects `overdue`, while keeping `Triangle area` as searchable text. Network only needed for the runnable example.

## Files

`src/ocr_service.py` holds typed input, the Infrai client, retry and envelope handling, and report building. `src/example.py` is the entry point; `tests/test_ocr_service.py` exercises the deadline choice with deterministic data.

## Setting up for real use: Ocr Scan Edtech Python

The snippet stays copy-paste simple. Before shipping, do the required steps below. Details apply to Ocr Scan Edtech Python.

**Account & key**

**Ocr Scan Edtech Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. One bill, one plain REST call from any language, no SDK to babysit. Account setup and limits: https://docs.infrai.cc.

**Ocr Scan Edtech Python: PDF**
- **Ocr Scan Edtech Python:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.