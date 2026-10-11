"""Adapt patch transport line endings to disposable workspace files."""

from pathlib import Path, PurePosixPath


def patch_bytes_for_workspace(root: Path, targets: tuple[str, ...], patch_text: str) -> bytes:
    """Encode a patch using the common existing newline style of its targets.

    Python text reads normalize newlines to ``\n``. On Windows, a copied
    repository may intentionally retain CRLF bytes, and Git requires patch
    context to use the same line endings. Only an all-CRLF target set is
    rewritten; mixed or LF repositories retain the original LF patch bytes.
    """
    existing_styles: set[bytes] = set()
    for target in targets:
        if target == "/dev/null":
            continue
        path = root.joinpath(*PurePosixPath(target).parts)
        if not path.is_file():
            continue
        data = path.read_bytes()
        if b"\r\n" in data:
            existing_styles.add(b"\r\n")
        elif b"\n" in data:
            existing_styles.add(b"\n")

    normalized = patch_text.replace("\r\n", "\n").replace("\r", "\n")
    if existing_styles == {b"\r\n"}:
        return normalized.replace("\n", "\r\n").encode("utf-8")
    return normalized.encode("utf-8")
