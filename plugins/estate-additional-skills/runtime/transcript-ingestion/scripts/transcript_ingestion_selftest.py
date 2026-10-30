#!/usr/bin/env python3
"""Selftest for deterministic transcript preservation and normalization."""

import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import normalize_transcript as transcript  # noqa: E402


passed = 0
failed = 0


def check(label, condition):
    global passed, failed
    if condition:
        passed += 1
        print("  PASS {}".format(label))
    else:
        failed += 1
        print("  FAIL {}".format(label))


def raises(label, error, function, *args, **kwargs):
    global passed, failed
    try:
        function(*args, **kwargs)
    except error:
        passed += 1
        print("  PASS {}".format(label))
    except Exception as other:
        failed += 1
        print("  FAIL {} raised {}".format(label, type(other).__name__))
    else:
        failed += 1
        print("  FAIL {} did not raise".format(label))


with tempfile.TemporaryDirectory() as directory:
    root = pathlib.Path(directory)
    source = root / "meeting.vtt"
    source.write_text(
        "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nJane: Start UAT Friday.\n"
        "Jane: Start UAT Friday.\n\n00:00:04.000 --> 00:00:05.000\nSam: Agreed.\n")
    before = source.read_bytes()
    result = transcript.ingest(
        source, root / "hub", "tx-2026-09-01-uat", "client-allison",
        "eng-2026-allison", "2026-09-01", "UAT working session", "Jane, Sam")
    raw = pathlib.Path(result["raw"])
    normalized = pathlib.Path(result["normalized"])
    text = normalized.read_text()
    check("raw bytes are preserved", raw.read_bytes() == before)
    check("normalized copy is Markdown", normalized.suffix == ".md")
    check("VTT timing is removed", "-->" not in text)
    check("consecutive duplicate caption is removed", text.count("Start UAT Friday") == 1)
    check("stable identity is present", 'context_id: "eng-2026-allison"' in text)
    check("context type is derived", 'context_type: "engagement"' in text)
    check("raw file is linked", 'raw_file: "../raw/tx-2026-09-01-uat.vtt"' in text)
    raises("repeat ingestion refuses overwrite", transcript.TranscriptError,
           transcript.ingest, source, root / "hub", "tx-2026-09-01-uat",
           "client-allison", "eng-2026-allison", "2026-09-01",
           "UAT working session")

    unsupported = root / "audio.mp3"
    unsupported.write_bytes(b"not audio")
    raises("unsupported input refuses", transcript.TranscriptError,
           transcript.ingest, unsupported, root / "hub", "tx-audio",
           "client-allison", "eng-2026-allison", "2026-09-01", "Audio")

    opportunity = root / "pursuit.txt"
    opportunity.write_text("Client wants an assessment.")
    pursuit = transcript.ingest(
        opportunity, root / "pursuit-hub", "tx-2026-09-01-discovery",
        "client-allison", "opp-2026-allison", "2026-09-01", "Discovery")
    check("opportunity transcripts are supported",
          'context_type: "opportunity"' in pathlib.Path(pursuit["normalized"]).read_text())

    unsafe = root / "unsafe.txt"
    unsafe.write_text("Unsafe identifier test.")
    raises("path-like transcript ID refuses", transcript.TranscriptError,
           transcript.ingest, unsafe, root / "unsafe-hub", "tx-/../../escape",
           "client-allison", "eng-2026-allison", "2026-09-01", "Unsafe")

    invalid = root / "invalid.txt"
    invalid.write_bytes(b"\xff")
    invalid_hub = root / "invalid-hub"
    raises("invalid UTF-8 refuses cleanly", transcript.TranscriptError,
           transcript.ingest, invalid, invalid_hub, "tx-invalid",
           "client-allison", "eng-2026-allison", "2026-09-01", "Invalid")
    check("failed normalization leaves no raw transcript",
          not (invalid_hub / "raw" / "tx-invalid.txt").exists())

    metadata = root / "metadata.txt"
    metadata.write_text("Metadata test.")
    metadata_result = transcript.ingest(
        metadata, root / "metadata-hub", "tx-metadata", "client-allison",
        "eng-2026-allison", "2026-09-01", "UAT: plan\nnext", "Jane: lead")
    metadata_text = pathlib.Path(metadata_result["normalized"]).read_text()
    check("frontmatter strings are safely quoted", 'participants: "Jane: lead"' in metadata_text)
    check("title newlines cannot inject frontmatter", 'title: "UAT: plan next"' in metadata_text)

print("{} passed, {} failed".format(passed, failed))
if failed:
    sys.exit(1)
