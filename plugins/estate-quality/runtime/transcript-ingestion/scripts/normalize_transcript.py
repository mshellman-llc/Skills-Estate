#!/usr/bin/env python3
"""Preserve a raw transcript and create a normalized Markdown copy."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import sys
import tempfile


SUPPORTED = {".md", ".txt", ".vtt"}
TIMING = re.compile(r"^\s*\d{2}:\d{2}(?::\d{2})?[.,]\d{3}\s+-->\s+.*$")
TRANSCRIPT_ID = re.compile(r"^tx-[a-z0-9][a-z0-9-]*$")
CLIENT_ID = re.compile(r"^client-[a-z0-9][a-z0-9-]*$")
CONTEXT_ID = re.compile(r"^(?:opp|eng)-[a-z0-9][a-z0-9-]*$")


class TranscriptError(Exception):
    pass


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def normalize_body(text: str, suffix: str) -> str:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    if suffix == ".vtt":
        cleaned = []
        for line in lines:
            stripped = line.strip()
            if stripped == "WEBVTT" or TIMING.match(line) or stripped.isdigit():
                continue
            if stripped and cleaned and cleaned[-1] == stripped:
                continue
            cleaned.append(stripped)
        lines = cleaned
    body = "\n".join(lines).strip()
    return body + "\n" if body else ""


def yaml_string(value: str) -> str:
    """Return a JSON-quoted string, which is also a valid YAML scalar."""
    return json.dumps(value, ensure_ascii=False)


def stage_file(directory: pathlib.Path, payload: bytes) -> pathlib.Path:
    descriptor, temporary = tempfile.mkstemp(prefix=".transcript-", dir=str(directory))
    path = pathlib.Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        path.unlink(missing_ok=True)
        raise
    return path


def ingest(source, destination, transcript_id, client_id, context_id,
           meeting_date, title, participants=""):
    source = pathlib.Path(source).expanduser().resolve()
    destination = pathlib.Path(destination).expanduser().resolve()
    if not source.is_file():
        raise TranscriptError("source is not a file: {}".format(source))
    suffix = source.suffix.lower()
    if suffix not in SUPPORTED:
        raise TranscriptError("unsupported transcript type: {}".format(suffix or "none"))
    if not TRANSCRIPT_ID.fullmatch(transcript_id):
        raise TranscriptError("transcript ID must be a lowercase tx- slug")
    if not CLIENT_ID.fullmatch(client_id):
        raise TranscriptError("client ID must be a lowercase client- slug")
    if not CONTEXT_ID.fullmatch(context_id):
        raise TranscriptError("context ID must be a lowercase opp- or eng- slug")
    context_type = "opportunity" if context_id.startswith("opp-") else "engagement"
    display_title = " ".join(title.split())
    if not display_title:
        raise TranscriptError("title must not be empty")

    source_bytes = source.read_bytes()
    try:
        source_text = source_bytes.decode("utf-8")
    except UnicodeDecodeError as error:
        raise TranscriptError("transcript is not valid UTF-8: {}".format(error))
    body = normalize_body(source_text, suffix)
    digest = sha256(source_bytes)

    raw_dir = destination / "raw"
    normalized_dir = destination / "normalized"
    raw_dir.mkdir(parents=True, exist_ok=True)
    normalized_dir.mkdir(parents=True, exist_ok=True)
    raw_target = raw_dir / "{}{}".format(transcript_id, suffix)
    markdown_target = normalized_dir / "{}.md".format(transcript_id)
    if raw_target.exists() or markdown_target.exists():
        raise TranscriptError("transcript already exists; refusing to overwrite")

    ingested = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    frontmatter = [
        "---",
        "transcript_id: {}".format(yaml_string(transcript_id)),
        "client_id: {}".format(yaml_string(client_id)),
        "context_id: {}".format(yaml_string(context_id)),
        "context_type: {}".format(yaml_string(context_type)),
        "meeting_date: {}".format(yaml_string(meeting_date)),
        "title: {}".format(yaml_string(display_title)),
        "participants: {}".format(yaml_string(participants)),
        "source_sha256: {}".format(yaml_string(digest)),
        "raw_file: {}".format(yaml_string("../raw/{}".format(raw_target.name))),
        "ingested_at: {}".format(yaml_string(ingested)),
        "---",
        "",
        "# {}".format(display_title),
        "",
    ]
    markdown_bytes = ("\n".join(frontmatter) + body).encode("utf-8")
    raw_staged = stage_file(raw_dir, source_bytes)
    markdown_staged = stage_file(normalized_dir, markdown_bytes)
    raw_published = False
    try:
        os.link(str(raw_staged), str(raw_target))
        raw_published = True
        os.link(str(markdown_staged), str(markdown_target))
    except FileExistsError:
        if raw_published:
            raw_target.unlink()
        raise TranscriptError("transcript already exists; refusing to overwrite")
    except Exception:
        if raw_published:
            raw_target.unlink()
        raise
    finally:
        raw_staged.unlink(missing_ok=True)
        markdown_staged.unlink(missing_ok=True)
    return {
        "raw": str(raw_target),
        "normalized": str(markdown_target),
        "source_sha256": digest,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("destination")
    parser.add_argument("--transcript-id", required=True)
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--context-id", required=True)
    parser.add_argument("--meeting-date", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--participants", default="")
    args = parser.parse_args(argv)
    try:
        result = ingest(
            args.source, args.destination, args.transcript_id, args.client_id,
            args.context_id, args.meeting_date, args.title, args.participants)
    except TranscriptError as error:
        print(str(error), file=sys.stderr)
        return 1
    print("raw: {}".format(result["raw"]))
    print("normalized: {}".format(result["normalized"]))
    print("source_sha256: {}".format(result["source_sha256"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
