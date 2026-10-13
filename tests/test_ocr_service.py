from datetime import date

from src.ocr_service import CourseDocument, build_learner_report, classify_deadline


def test_report_marks_past_deadline_and_keeps_ocr_text() -> None:
    document = CourseDocument("Lin", "Geometry", date(2026, 9, 1), "scan.pdf")
    report = build_learner_report(document, {"text": "Triangle area"}, date(2026, 9, 4))
    assert report["deadline_status"] == "overdue"
    assert report["searchable_text"] == "Triangle area"
    assert classify_deadline(date(2026, 9, 8), date(2026, 9, 4)) == "upcoming"
