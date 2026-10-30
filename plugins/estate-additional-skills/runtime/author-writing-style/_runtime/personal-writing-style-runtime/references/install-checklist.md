# Install checklist

What a per-person adapter must confirm before it goes live, and what it must
never contain.

## Required, per install

- `profile_path`: where the confirmed profile lives, outside this
  repository, per the writing-style-builder schema.
- `person_id`: matches `person_id` in that profile file.
- `authorized_surfaces`: which runtimes this install is cleared to run on,
  such as Claude Code, claude.ai, Cowork, or others. An install does not
  assume every surface by default.
- A check, run before first use and on every profile update, that
  `authorization.granted` is true and `revoked` is false. An adapter must
  refuse to apply voice against a profile that fails either check.

## Never in an install file

- The profile content itself: tendencies, overlays, examples. The install
  points at the profile; it does not embed it.
- Raw evidence or anything resembling it.
- A hardcoded fallback to another person's profile in case this one is
  missing. A missing or revoked profile means plain, unstyled drafting,
  never a silent substitution.

## Estate integration

Follow `skill-estate-sync` conventions for building a surface-specific
adapter for each runtime an install targets: the terminal, a browser-based
assistant, a shared workspace tool, or an API integration. This runtime
template itself ships in `house-skills`; a person's
install configuration and their profile never do. Record a manual
publication the same way `skill-estate-sync` records any other manual
surface step. Do not claim a cloud surface was updated without having
verified it there.
