"""Frozen predicates from the two source instruments listed in PROTOCOL.md."""

INVISIBLE_CODEPOINTS = {
    0x200B,
    0x200C,
    0x200D,
    0x200E,
    0x200F,
    0xFEFF,
    0x2060,
    0x2061,
    0x2062,
    0x2063,
    0x2064,
    0x2066,
    0x2067,
    0x2068,
    0x2069,
    0x202A,
    0x202B,
    0x202C,
    0x202D,
    0x202E,
}

ELLIPSIS_FORMS = {".", "..", "...", "....", "…", "…."}


def near_void(text: str) -> bool:
    if not text:
        return False
    if all(
        ord(character) in INVISIBLE_CODEPOINTS or character.isspace()
        for character in text
    ):
        return True
    return text.strip() in ELLIPSIS_FORMS


def explicit_block(obj):
    markers = {"blocked", "safety_block", "filtered", "blocked_by_safety"}

    def nested(value):
        if isinstance(value, dict):
            return any(
                k in markers and v is True or nested(v) for k, v in value.items()
            )
        if isinstance(value, list):
            return any(nested(v) for v in value)
        return False

    return any(
        (k in markers and v is True)
        or (any(s in k.lower() for s in ("safety", "filter", "block")) and nested(v))
        for k, v in obj.items()
    )
