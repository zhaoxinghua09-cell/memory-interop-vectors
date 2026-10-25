#!/usr/bin/env python3
"""Check a retention record (catalogue item 6) against the LGD three laws.

Usage:
    python check_retention.py retention_record.example.yaml
    echo exit code: 0 = PASS, 1 = FAIL

Each check prints a line with a three-law prefix:
    [LGD-I identity]  / [LGD-II evidence]  / [LGD-III governance]
The complete example must PASS; the two deliberately-incomplete records
must FAIL, proving the check can fail (a falsifiable gate).
"""
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required for this check: pip install pyyaml")


def get(d, path):
    cur = d
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def check(rec):
    results = []

    def add(law, name, ok, detail=""):
        results.append((ok, f"[{law}] {name}: {'PASS' if ok else 'FAIL'}{(' - ' + detail) if detail else ''}"))

    # LGD-I identity: named owner, explicit revision, change traceability
    identity = get(rec, ["record", "identity"]) or {}
    add("LGD-I", "owner named", bool(identity.get("owner")))
    add("LGD-I", "explicit revision identity", bool(identity.get("revision")))
    add("LGD-I", "approval named", bool(get(rec, ["record", "approval", "approved_by"])))

    changes = get(rec, ["record", "changes"]) or []
    change_ok = any(c.get("authority") and c.get("prior_value") for c in changes)
    add("LGD-I", "a correction is attributable and prior value recoverable", change_ok)

    # NOTE: "in_charter_section_3" means whether the regime is *explicitly
    # named* in the §3 crosswalk. The retention legs are not named; GDPR 17 is.
    # The Chair reads the bracketed four as examples and counts MDR/820/ISO
    # 13485 as "comparable regimes" (a broad reading the author shares).
    #
    # LGD-II evidence: the two retention legs + the erasure boundary,
    # each tied to a named, verifiable regime
    retention = get(rec, ["record", "retention"]) or {}
    legs = retention.get("legs") or []
    eu = [l for l in legs if "MDR" in str(l.get("regime", ""))]
    us = [l for l in legs if "820" in str(l.get("regime", "")) or "QMSR" in str(l.get("regime", ""))]
    add("LGD-II", "EU retention leg (MDR 10(8)) not explicitly named in §3", bool(eu) and eu[0].get("in_charter_section_3") is False)
    add("LGD-II", "US retention leg (QMSR / ISO 13485) not explicitly named in §3", bool(us) and us[0].get("in_charter_section_3") is False)

    erasure = get(rec, ["record", "erasure"]) or {}
    erasure_ok = "17(3)(b)" in str(erasure.get("regime", "")) and erasure.get("in_charter_section_3") is True
    add("LGD-II", "erasure boundary (GDPR 17(3)(b), explicitly named in §3)", erasure_ok)

    # LGD-III governance: retention legs are not explicitly named in the
    # §3 crosswalk (reached only via the broad "comparable regimes" reading),
    # and the record is retrievable on demand without reconstruction
    add("LGD-III", "retention legs not explicitly named in charter §3",
        retention.get("in_charter_section_3") is False)
    add("LGD-III", "retrievable on demand without reconstruction",
        bool(get(rec, ["record", "retrievability", "produced_without_reconstruction"])))

    return results


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: python check_retention.py <record.yaml>")
    with open(sys.argv[1], "r", encoding="utf-8") as fh:
        rec = yaml.safe_load(fh)

    results = check(rec)
    for _, line in results:
        print(line)
    failed = sum(1 for ok, _ in results if not ok)
    print(f"\n{len(results)} checks, {failed} failed")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
