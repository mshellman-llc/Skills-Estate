# Commons Clause rewrites

This record lists each estate skill rewritten to remove third-party material whose license bars its sale. For each skill it gives the date, the pull request, the method and the result of an overlap audit. Each later rewrite adds its own section.

## Background

Five skills adapted material from the Claude Skills Library by Amin Borghei, published at https://github.com/borghei/Claude-Skills and adopted from commit 2c12c7efaad13a70bdea6e205698a6c4f93a0682. That library is licensed under MIT with the Commons Clause License Condition v1.0. The condition withholds the right to sell the software, which covers a product or service whose value derives entirely or substantially from it. Under the [skill standard](../../policies/skill-standard.md), the catalog marks such a skill as not for sale until it is rewritten without the upstream material or licensed.

On 2026-11-09 the owner decided to rewrite all five as original work, one pull request per skill. A rewrite removes the skill's copy of the upstream license, its provenance file and its not-for-sale mark. Whether anything built on these skills may be sold is a question for legal review. This record documents the engineering method and its results for that review and is not a legal opinion.

## Method

Each rewrite follows three steps. AI agents working for the owner carry them out, and the owner approves each merge.

1. **Specification.** The estate's development agent reads the old skill, its tests and every estate file that calls it. It then writes a functional specification outside the repository: purpose, inputs, outputs, command-line interface, rules, hand-offs and test requirements, kept to facts and interfaces in note form. Names that other estate files depend on stay identical, such as script paths, flags, JSON keys, exit codes and method names. Before hand-off, the specification is itself compared with the old files and the upstream files.
2. **Fresh write.** A separate agent instance receives only the specification, the target paths and the estate's writing rules. It works in a copy of the repository without the repository's Git history. Every copy of the old skill is removed from that copy first: the skill folder, its packaged plugin copy, the generated skills-map data and any recorded example run. The writer is told to read nothing outside its copy, use no network and look for no existing implementation. These limits are instructions only. Nothing blocks the writer from the network. The machine it runs on also holds the upstream checkout and the previous skill files. Its report lists any departure from the limits. The audit in step 3 then checks the result.
3. **Overlap audit.** A script compares every new file with (a) every file in the upstream skill folder, including those the old provenance record listed, and (b) every file the skill held at the last revision before the rewrite. It reports each shared run of 8 or more words in prose, or 6 or more tokens in code, after lowercasing. Interface identifiers, method and formula names, standard terms, numbers in prose, and punctuation, keywords and built-in names in code add nothing to a run's length, though they must still match for the run to continue. Each flagged passage is rewritten and the audit repeated until nothing is flagged.

The scoring methods themselves are published ideas: RICE, ICE, WSJF, the Opportunity Score, ODI, Kano, MoSCoW and the Eisenhower matrix. The new text explains them in its own words and credits their originators.

## prioritize-work

Rewritten on 2026-11-09 in [pull request 68](https://github.com/mshellman-llc/Skills-Estate/pull/68) and recorded as plugin version 0.4.5.

The old skill adapted these upstream files from `project-management/execution/prioritization-frameworks/` at the commit named above:

| SHA-256 at adoption | Upstream file |
| --- | --- |
| 1e6a0ec869145ac36762604849ffe6e3fc8e12ab5e966893fb864cf794e57756 | `SKILL.md` |
| 03d29678803d13eb5e2789a069d9a2c14b2d1cc92fb0f6e240c2480ff47b0209 | `scripts/prioritization_scorer.py` |
| 1b67683fa4038fd4eeab654381ae4aa51d001fa45b86dd5e5816b98ea952c040 | `references/frameworks-catalog.md` |
| 5c7ddb43a3c1bf04451baef80f65b78221f792973c30dad99f303a8670d364be | `references/prioritization-guide.md` |
| 778d61a5b02715b1d66b088e54f1cbaa94c42c8fa11b75e0cefeeb3c05f8bb00 | `references/red-flags.md` |

What changed:

- All of the skill's files are new: `SKILL.md`, three references, the scorer, its selftest and 12 fixtures describing an invented ferry booking app. The old example data is gone, including the upstream demo items and scores that the old selftest reproduced.
- The same pull request deletes `LICENSE-UPSTREAM` and `UPSTREAM.md` and drops the skill's `license` and `commercial_use` entries from the catalog.
- Interfaces stayed the same: the scorer's path, its `--framework` values, its JSON report keys and its exit codes.

Audit result:

- The specification shared at most 4 consecutive counted words with any old or upstream file.
- On the first run against the fresh write, 7 passages were flagged, all prose and all shared with the old estate version. None was shared with upstream. The longest ran to 14 words.
- After those passages were rewritten, nothing was flagged. Three more passages that shared 7 words, just under the threshold, were reworded as well. The longest remaining run of counted words is 4 against upstream and 6 against the old version, a standard definition of risk. In code, no shared run holds more than 3 counted tokens.
- For comparison, the old version had no flagged run against upstream either; at most 5 counted words in a row matched. What it did carry from upstream was a worked example for the Opportunity Score and a demo data set of five candidates with their scores. The rewrite replaces both.
- Twice during the write, a text search passed over the folders of the four skills that still carry the upstream license. Their output was filtered out and no file there was opened. A file listing also showed the names of some fixture files in two of those folders, without their contents. The audit compared the new files with those four skills as well and found no flagged run.
- A second comparison, run separately, counted every token, identifiers and numbers included. It covered the old version, the four restricted skills and the whole upstream `project-management` tree of 582 files. Every match at least 8 tokens long was an interface name, the RICE impact scale, the standard WSJF terms, the estate's shared build-card pointer or a common Python idiom.
