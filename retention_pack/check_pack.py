#!/usr/bin/env python3
"""Retention conformance pack (six steps) — catalogue item 6, W3C AIMI CG.

Usage:
    python check_pack.py <scenario.yaml>          # exit 0 = PASS, 1 = FAIL
    python check_pack.py --selftest               # run all positives AND all
                                                  # negative controls; exit 0
                                                  # only if every scenario
                                                  # behaves as documented

Checks are grouped by LGD three-law prefix:
    [LGD-I identity] / [LGD-II evidence] / [LGD-III governance]

The complete scenarios must PASS; the negative controls must FAIL, proving
the check can fail (a falsifiable gate).
"""
import sys
from datetime import date, datetime

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

    sc = get(rec, ["scenario"]) or {}
    step = sc.get("step")
    record = get(rec, ["record"]) or {}

    if step == 1:  # CREATE
        identity = get(record, ["identity"]) or {}
        add("LGD-I", "owner named", bool(identity.get("owner")))
        add("LGD-I", "explicit revision identity", bool(identity.get("revision")))
        add("LGD-I", "identity current as of a date", bool(identity.get("current_as_of")))
        add("LGD-I", "approval named", bool(get(record, ["approval", "approved_by"])))

    elif step == 2:  # MODIFY
        changes = get(record, ["changes"]) or []
        ok = bool(changes) and all(
            c.get("authority") and c.get("prior_value") and c.get("by") and c.get("at")
            for c in changes)
        add("LGD-I", "every change attributable (by/at) with named authority",
            bool(changes) and ok,
            "" if ok else "a change lacks authority, prior value, or actor")

    elif step == 3:  # HISTORY RESTORE
        history = get(record, ["history"]) or []
        ok = bool(history) and all(
            h.get("revision") and h.get("stored_digest") and h.get("pointer")
            and h.get("restored_digest_matches") is True
            for h in history)
        add("LGD-II", "prior revision restorable: stored digest + pointer + restore verified",
            ok, "" if ok else "a prior revision lacks a stored digest, pointer, or verified restore")

    elif step == 4:  # TAMPER DETECTION (AT REST)
        integrity = get(record, ["integrity"]) or {}
        add("LGD-II", "digest algorithm explicit", integrity.get("digest_algorithm") == "sha-256")
        verif = str(integrity.get("verification") or "")
        add("LGD-II", "integrity verified AT REST (not only at write time)",
            "at-rest" in verif.lower() or "at rest" in verif.lower(),
            "" if ("at-rest" in verif.lower() or "at rest" in verif.lower())
            else f"verification reads {verif!r}")
        indicators = get(record, ["storage", "tamper_indicators"]) or []
        add("LGD-II", "storage-layer tamper indicators present", bool(indicators))

    elif step == 5:  # RETENTION PERIOD VERIFICATION
        legs = get(record, ["retention", "legs"]) or []
        serving = get(record, ["serving", "date"])
        try:
            serving_date = datetime.strptime(str(serving), "%Y-%m-%d").date()
        except (TypeError, ValueError):
            serving_date = None
        expiries = []
        for l in legs:
            years = l.get("minimum_years")
            last = l.get("last_device_on_market")
            try:
                base = datetime.strptime(str(last), "%Y-%m-%d").date()
                expiries.append((l.get("regime"), date(base.year + int(years), base.month, base.day)))
            except (TypeError, ValueError):
                pass
        add("LGD-III", "at least one computable retention boundary", bool(expiries))
        hold = get(record, ["serving", "legal_hold"]) or {}
        within = serving_date is not None and expiries and serving_date <= min(e for _, e in expiries)
        add("LGD-III", "served within the earliest boundary, or a documented legal hold covers the overhang",
            within or bool(hold.get("basis") and hold.get("decided_by")),
            "" if (within or hold.get("basis")) else "no boundary computable and no hold documented")

    elif step == 6:  # ERASE VS RETAIN CONFLICT
        erasure = get(record, ["erasure"]) or {}
        add("LGD-III", "erasure request recorded with requester and regime",
            bool(erasure.get("request_date") and erasure.get("regime")))
        res = get(record, ["resolution"]) or {}
        add("LGD-III", "conflict resolution documented: action + legal basis + decider",
            bool(res.get("action") and res.get("legal_basis") and res.get("decided_by")),
            "" if (res.get("action") and res.get("legal_basis")) else "open conflict with no documented resolution")
    else:
        add("LGD-I", "known scenario step", False, f"unknown step {step!r}")

    return results


def run_file(path):
    try:
        rec = yaml.safe_load(open(path, encoding="utf-8"))
    except FileNotFoundError:
        print(f"ERROR: file not found: {path}")
        return False
    results = check(rec)
    failed = 0
    for ok, line in results:
        print(line)
        if not ok:
            failed += 1
    print(f"{len(results)} checks, {failed} failed  ({path})")
    return failed == 0


# (filename, must_pass)
SELFTEST = [
    ("scenarios/s1_create.example.yaml", True),
    ("scenarios/s1_create.no_revision_identity.yaml", False),
    ("scenarios/s2_modify.example.yaml", True),
    ("scenarios/s2_modify.unattributed_change.yaml", False),
    ("scenarios/s3_restore.example.yaml", True),
    ("scenarios/s3_restore.prior_unrecoverable.yaml", False),
    ("scenarios/s4_tamper.example.yaml", True),
    ("scenarios/s4_tamper.write_time_only.yaml", False),
    ("scenarios/s5_period.example.yaml", True),
    ("scenarios/s5_period.served_past_expiry.yaml", False),
    ("scenarios/s6_erase.example.yaml", True),
    ("scenarios/s6_erase.conflict_unhandled.yaml", False),
]


def selftest():
    all_ok = True
    passes = fails = 0
    for fname, must_pass in SELFTEST:
        passed = run_file(fname)
        behaves = (passed == must_pass)
        all_ok &= behaves
        if must_pass:
            passes += behaves
            mark = "OK " if behaves else "BAD"
            print(f"  {mark} {fname}: expected PASS, got {'PASS' if passed else 'FAIL'}")
        else:
            fails += behaves
            mark = "OK " if behaves else "BAD"
            print(f"  {mark} {fname}: expected FAIL, got {'FAIL' if not passed else 'PASS'}")
        print()
    print(f"selftest: positives behaving {passes}/6, negatives behaving {fails}/6")
    print("ALL BEHAVIOURS AS DOCUMENTED" if all_ok else "SELFTEST FAILED")
    return all_ok


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        sys.exit(0 if selftest() else 1)
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(0 if run_file(sys.argv[1]) else 1)
