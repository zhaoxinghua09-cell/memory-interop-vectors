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

    # ---- ADEQUACY (added 2026-10-29 after red-team) ----
    # v1 of this gate checked only that a `minimum_years` field EXISTED.
    # Red-team proof: setting EU 10→3, implantable 15→3, US 2→1 still produced
    # "9 checks, 0 failed". The gate was falsifiable in form and unfalsifiable
    # in substance — it was checking presence, not adequacy, which is exactly
    # the defect this catalogue entry exists to name.
    #
    # The floors are hard-coded on purpose: the criterion belongs to the law,
    # not to the record being checked. Letting the record declare its own floor
    # would be self-certification (cf. §2.2 OCSP "unknown" not being "good").
    #   EU  MDR 2017/745 Art. 10(8): >= 10 years; >= 15 for implantables
    #   US  21 CFR 820.35 incorporates ISO 13485 Cl. 4.2.5 by reference
    #       (§ 820.7), which sets the period; § 820.35 itself states no period.
    EU_FLOOR, EU_IMPLANT_FLOOR, US_FLOOR = 10, 15, 2

    def floor_check(label, leg, key, floor):
        v = leg.get(key) if leg else None
        ok = isinstance(v, int) and v >= floor
        add("LGD-II", f"{label} >= {floor} years (statutory floor)",
            ok, f"declared {v!r}")

    floor_check("EU retention period", eu[0] if eu else None, "minimum_years", EU_FLOOR)
    floor_check("EU implantable period", eu[0] if eu else None, "implantable_years", EU_IMPLANT_FLOOR)
    floor_check("US retention period", us[0] if us else None, "minimum_years", US_FLOOR)

    # ---- SECOND LIMB (added 2026-10-29, closing the gap flagged as 待核实) ----
    # The US period is not only ">= 2 years"; it is also "not less than the
    # lifetime of the device as defined by the organization". The first red-team
    # round only covered the floor, so a record declaring a 2-year period for a
    # 12-year implantable device still passed — the same presence-vs-adequacy
    # defect, one limb down.
    #
    # VERIFIED 2026-10-29 against the eCFR text of § 820.35 (Cornell LII mirror,
    # https://www.law.cornell.edu/cfr/text/21/820.35): the section opens
    # "In addition to the requirements of Clause 4.2.5 in ISO 13485 (incorporated
    # by reference, see § 820.7), Control of Records, ..." and then lists only
    # what certain records must contain. It states NO retention period.
    #
    # NOT VERIFIED: the verbatim wording of ISO 13485 Cl. 4.2.5 (paywalled).
    # Therefore this check compares the declared retention against the DECLARED
    # device lifetime; it does not certify the lifetime figure itself. An
    # implementer must be able to show where the lifetime came from.
    def lifetime_check(leg):
        if not leg:
            add("LGD-II", "US retention >= device expected life", False, "no US leg")
            return
        life = leg.get("device_lifetime_years")
        keep = leg.get("minimum_years")
        ok = isinstance(life, int) and isinstance(keep, int) and keep >= life
        add("LGD-II", "US retention >= device expected life", ok,
            f"retention {keep!r}, device life {life!r}")

    lifetime_check(us[0] if us else None)

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
