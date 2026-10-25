# Legal Sources — Primary Evidence for the Retention Record (catalogue item 6)

Every legal citation in the retention record is traced to a primary
official source below. Each entry gives the official link and the
controlling text. No citation relies on a private or local copy; a
reviewer can open the official source and verify it independently.

---

## 1. EU MDR 2017/745 — Article 10(8) (retention leg; not explicitly named in charter §3)

- **Official source**: EUR-Lex, Regulation (EU) 2017/745 (CELEX 32017R0745) —
  https://eur-lex.europa.eu/eli/reg/2017/745/oj
- **Controlling text**: the technical documentation and the EU declaration
  of conformity shall be kept at the disposal of the competent authorities
  for at least **10 years** after the last device has been placed on the
  market, and for at least **15 years** in the case of implantable devices.

## 2. US QMSR — 21 CFR Part 820 with ISO 13485 (retention leg; not explicitly named in charter §3)

- **Official source**: eCFR, Title 21, Part 820 —
  https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-820
- **§820.7 Incorporation by reference (b)**: ISO 13485:2016(E), *Medical
  devices — Quality management systems — Requirements for regulatory
  purposes*, is incorporated by reference.
- **§820.35 Control of records**: "In addition to the requirements of
  Clause 4.2.5 in ISO 13485 (incorporated by reference, see §820.7), Control
  of Records, the manufacturer must include the following information in
  certain records..." — i.e. §820.35 is a record-control provision added
  **to** ISO 13485 Clause 4.2.5 and does not itself state the retention period.
- **Where the period now lives**: ISO 13485:2016 Clause 4.2.5 (Control of
  records), incorporated via §820.7. It requires records to be retained for
  at least the lifetime of the medical device as defined by the organization,
  or as specified by applicable regulatory requirements, **but not less than
  two years from the medical device release by the organization** — the same
  two-year floor the prior QSR carried.

## 3. Prior QSR — the record-retention rule before QMSR

- **Historical source**: eCFR point-in-time version of 21 CFR Part 820
  (pre-QMSR) —
  https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-820
- **Controlling text**: records required by the part were to be retained for
  a period equivalent to the design and expected life of the device, but in
  no case less than **2 years** from the date of release for commercial
  distribution. QMSR superseded that record-retention rule with ISO 13485
  Clause 4.2.5 incorporated by reference.

## 4. GDPR — Article 17(3)(b) (erasure boundary; explicitly named in charter §3)

- **Official source**: EUR-Lex, Regulation (EU) 2016/679 (CELEX 32016R0679) —
  https://eur-lex.europa.eu/eli/reg/2016/679/oj
- **Controlling text**: the right to erasure in paragraph 1 does not apply,
  under paragraph 3(b), to the extent processing is necessary for compliance
  with a legal obligation to which the controller is subject under Union or
  Member State law.
- **What it does not settle**: it resolves the collision in law but not in
  the store; the store must still show that what it kept is what the
  obligation covers and that what it removed is outside it.

---

## Charter §3 crosswalk — inside vs. outside

| Leg | Regime | Explicitly named in charter §3? |
|---|---|---|
| Retention (EU) | MDR 2017/745 Art. 10(8) | **No** |
| Retention (US) | 21 CFR Part 820 / ISO 13485 Cl. 4.2.5 | **No** |
| Erasure | GDPR Art. 17(3)(b) | **Yes** |

The four bracketed examples in §3 are read (by the Chair and the author) as
examples rather than a closed list, so the medical-device rules count as
"comparable regimes" under that broad reading; the author shares that reading
and does not ask to reopen §3.

---

## How to reproduce the check

```bash
# from the repository root:
python retention/check_retention.py retention/retention_record.example.yaml        # exit 0, 9/9 PASS
python retention/check_retention.py retention/retention_record.missing_us_leg.yaml # exit 1, US leg FAIL
python retention/check_retention.py retention/retention_record.no_erasure.yaml      # exit 1, erasure FAIL
```

The two failing records demonstrate the gate is falsifiable.
