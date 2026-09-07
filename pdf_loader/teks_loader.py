"""Ekstrak teks dari PDF digital ke TXT atau Markdown tanpa OCR."""

import argparse
from pathlib import Path

import pymupdf4llm


def extract_text(input_pdf: Path, output_file: Path, output_format: str) -> Path:
    """Membaca PDF digital dan menyimpan teks hasil ekstraksi."""
    if not input_pdf.is_file():
        raise FileNotFoundError(f"File PDF tidak ditemukan: {input_pdf}")

    if input_pdf.suffix.lower() != ".pdf":
        raise ValueError("File input harus berformat .pdf")

    # OCR sengaja dimatikan. PDF hasil scan dapat menghasilkan teks kosong.
    if output_format == "md":
        extracted_text = pymupdf4llm.to_markdown(
            str(input_pdf),
            use_ocr=False,
            show_progress=True,
        )
    else:
        extracted_text = pymupdf4llm.to_text(
            str(input_pdf),
            use_ocr=False,
            show_progress=True,
        )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(extracted_text, encoding="utf-8")
    return output_file


def build_parser() -> argparse.ArgumentParser:
    """Membuat daftar argumen command line."""
    parser = argparse.ArgumentParser(
        description="Ekstrak teks PDF digital tanpa OCR memakai PyMuPDF4LLM."
    )
    parser.add_argument("input_pdf", type=Path, help="Lokasi file PDF yang dibaca")
    parser.add_argument(
        "-f",
        "--format",
        choices=("txt", "md"),
        default="txt",
        help="Format hasil: txt (default) atau md",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Lokasi file hasil; default: output/<nama-pdf>.<format>",
    )
    return parser


def main() -> None:
    input_pdf = Path("input_pdf/Pedoman PI.pdf")
    output_file = Path("output/Pedoman PI.md")
    output_format = "md"

    try:
        saved_file = extract_text(
            input_pdf=input_pdf,
            output_file=output_file,
            output_format=output_format,
        )
    except (FileNotFoundError, ValueError, OSError, RuntimeError) as error:
        raise SystemExit(f"Gagal: {error}") from error

    print(f"Selesai. Hasil disimpan di: {saved_file.resolve()}")


if __name__ == "__main__":
    main()