import base64
from datetime import date

from ocr_service import CourseDocument, InfraiPdfClient, process_document


def sample_pdf() -> str:
    stream = b"BT /F1 18 Tf 50 100 Td (Algebra foundations) Tj ET"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 160] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return base64.b64encode(pdf).decode("ascii")


def main() -> None:
    document = CourseDocument(
        learner="Aisha Khan",
        course="Algebra foundations",
        deadline=date(2026, 9, 12),
        pdf=sample_pdf(),
    )
    report = process_document(document, InfraiPdfClient(), date.today())
    print(report)


if __name__ == "__main__":
    main()
