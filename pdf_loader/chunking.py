import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INPUT_TEXT = BASE_DIR / "output/Pedoman PI_cleaned.txt"
OUTPUT_FILE = BASE_DIR / "output/Pedoman PI_chunks.json"
CHUNK_SIZE = 480
CHUNK_OVERLAP = 96


def chunk_text(
    extracted_text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """Potong teks per jumlah kata; spasi dan baris baru dirapikan menjadi spasi."""
    if chunk_size <= 0:
        raise ValueError("chunk_size harus lebih besar dari 0.")
    if not 0 <= chunk_overlap < chunk_size:
        raise ValueError("chunk_overlap harus >= 0 dan lebih kecil dari chunk_size.")

    words = extracted_text.split()
    chunks: list[str] = []
    step = chunk_size - chunk_overlap

    for start in range(0, len(words), step):
        end = start + chunk_size
        chunks.append(" ".join(words[start:end]))

        if end >= len(words):
            break

    return chunks


def split_document(extracted_text: str) -> tuple[str, str]:
    """Pisahkan daftar isi dari isi utama pada heading Pendahuluan pertama."""
    body_heading = re.search(
        r"(?m)^1\. PENDAHULUAN\s*$",
        extracted_text,
    )
    if body_heading is None:
        raise ValueError("Batas isi utama '1. PENDAHULUAN' tidak ditemukan.")

    table_of_contents = extracted_text[: body_heading.start()].strip()
    body = extracted_text[body_heading.start() :].strip()
    return table_of_contents, body


def main() -> None:
    """Baca hasil ekstraksi, lakukan chunking, lalu ekspor chunk ke JSON."""
    try:
        cleaned_text = INPUT_TEXT.read_text(encoding="utf-8")
        table_of_contents, body = split_document(cleaned_text)

        sections = {
            "daftar_isi": table_of_contents,
            "isi_utama": body,
        }
        records = []

        for content_type, section_text in sections.items():
            section_chunks = chunk_text(
                section_text,
                CHUNK_SIZE,
                CHUNK_OVERLAP,
            )

            for section_index, text in enumerate(section_chunks, start=1):
                records.append(
                    {
                        "chunk_index": len(records) + 1,
                        "section_chunk_index": section_index,
                        "content_type": content_type,
                        "source": INPUT_TEXT.name,
                        "word_count": len(text.split()),
                        "text": text,
                    }
                )

        if not records:
            raise ValueError("File teks kosong. Periksa hasil ekstraksi terlebih dahulu.")

        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_FILE.write_text(
            json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except (OSError, UnicodeError, ValueError) as error:
        raise SystemExit(f"Gagal: {error}") from error

    toc_count = sum(record["content_type"] == "daftar_isi" for record in records)
    body_count = len(records) - toc_count
    print(f"Selesai. {len(records)} chunk disimpan di: {OUTPUT_FILE}")
    print(f"Daftar isi: {toc_count} chunk; isi utama: {body_count} chunk.")
    print(f"Ukuran: {CHUNK_SIZE} kata; overlap: {CHUNK_OVERLAP} kata.")


if __name__ == "__main__":
    main()
