import re
import hashlib


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def get_post_hash(text: str) -> str:
    normalized = normalize_text(text)

    return hashlib.md5(
        normalized.encode("utf-8")
    ).hexdigest()


def remove_anonymous_marker(text: str):
    pattern = re.compile(
        r"(?i)(#анонимно|анонимно)"
    )

    anonymous = bool(
        pattern.search(text)
    )

    cleaned = pattern.sub("", text)

    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned
    ).strip()

    return cleaned, anonymous
