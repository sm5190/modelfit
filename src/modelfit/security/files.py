from pathlib import Path

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".txt", ".docx"}
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024


def validate_upload(filename: str, size_bytes: int) -> None:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix}")
    if size_bytes > MAX_FILE_SIZE_BYTES:
        raise ValueError("File exceeds the 25 MB upload limit.")
