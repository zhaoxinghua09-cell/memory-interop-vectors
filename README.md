# Memory Interop Vectors

Self-contained, independently verifiable record vectors for the W3C
AI Agent Memory Interoperability Community Group use-case catalogue.

Each vector is a worked record plus a small, dependency-light checker.
The complete example must PASS; the deliberately incomplete records
must FAIL, so a reviewer (human or AI) can confirm the check is real
and falsifiable rather than a script that always reports success.

## Vectors

| Catalogue item | Vector | What it verifies |
|---|---|---|
| 6. Retention (Xinghua, 22 October) | [retention/](retention/) | whether the record served years later is the record written on the day, and where the keeping/erasure boundary falls |

## How to verify

```bash
# complete example (expect 9/9 PASS, exit 0)
python retention/check_retention.py retention/retention_record.example.yaml

# negative controls (expect FAIL, exit 1)
python retention/check_retention.py retention/retention_record.missing_us_leg.yaml
python retention/check_retention.py retention/retention_record.no_erasure.yaml
```

Requires Python 3 and PyYAML (`pip install pyyaml`). Exit code 0 = PASS,
1 = FAIL.

## Provenance and scope

Maintained by Xinghua Zhao (Independent researcher), ORCID
0009-0001-0512-1237. Every legal citation is traced to a primary
official source in `retention/legal_sources.md`. These vectors make the
record fields machine-checkable; they do not assert that the charter
itself is legally true, and they are not legal or regulatory advice.

AI disclosure: drafted with AI assistance from sources read by the
maintainer; the reading and the position are the maintainer's.
