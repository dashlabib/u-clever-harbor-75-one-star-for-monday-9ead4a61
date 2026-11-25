"""Validate the one-star Monday review and copy it to the output path.

The review lives in entry.txt next to this script. This program reads
those exact bytes, checks them against the competition gate (UTF-8
text, 1 to 180 characters, not only whitespace) plus the bounty rules
(a single line, at most 25 words, no trailing whitespace, all
printable), writes the unchanged bytes to /output/entry.txt, and then
re-reads the file it wrote and refuses to finish if even one byte
differs. Running it twice always produces identical output.
"""

import os
import sys


def fail(message):
    print("error: " + message, file=sys.stderr)
    raise SystemExit(1)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(here, "entry.txt")

    try:
        with open(source_path, "rb") as handle:
            raw = handle.read()
    except OSError as exc:
        fail("cannot read entry.txt: " + str(exc))

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        fail("entry.txt is not valid UTF-8")

    if not 1 <= len(text) <= 180:
        fail("entry must be 1 to 180 characters, got %d" % len(text))
    if text.strip() == "":
        fail("entry must not be only whitespace")
    if "\n" in text or "\r" in text:
        fail("entry must be a single line")
    if text != text.strip():
        fail("entry must not have leading or trailing whitespace")

    words = text.split()
    if len(words) > 25:
        fail("entry must be at most 25 words, got %d" % len(words))
    if any(not ch.isprintable() for ch in text):
        fail("entry must contain only printable characters")

    # Report each gate rule before writing, so a failed or
    # surprising run names the rule instead of failing silently.
    checks = [
        ("utf-8", "decoded as UTF-8"),
        ("length", "%d characters (need 1 to 180)" % len(text)),
        ("non-blank", "more than white space"),
        ("single-line", "one line, no line break"),
        ("no-edge-space", "no leading or trailing whitespace"),
        ("words", "%d words (at most 25)" % len(words)),
        ("printable", "printable characters only"),
    ]
    for name, detail in checks:
        print("gate %s: %s" % (name, detail), file=sys.stderr)

    target = "/output/entry.txt"
    try:
        os.makedirs("/output", exist_ok=True)
        with open(target, "wb") as handle:
            handle.write(raw)
    except OSError:
        target = os.path.join(here, "output_entry.txt")
        try:
            with open(target, "wb") as handle:
                handle.write(raw)
        except OSError as exc:
            fail("cannot write output: " + str(exc))

    try:
        with open(target, "rb") as handle:
            written = handle.read()
    except OSError as exc:
        fail("cannot re-read output: " + str(exc))
    if written != raw:
        fail("output bytes differ from entry.txt")

    print("wrote %d bytes (%d words) to %s" % (len(raw), len(words), target))


if __name__ == "__main__":
    main()
