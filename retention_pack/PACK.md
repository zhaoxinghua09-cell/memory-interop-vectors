# Retention Conformance Pack — Six-Step Test Skeleton (draft v0.1)

> **一句话结论**：这是 catalogue item 6（Retention）的六步一致性测试骨架——每步一个可跑正例（必须 PASS）加一个可证伪负对照（必须 FAIL），把"同一条记录多年后取回仍相同、且留/删边界可判定"从用例叙述变成机器可查结构；它是结构骨架与工作示例，不是对任何具体记忆产品的实现级测试。

- 状态：**proposed contribution**，not agreed text of the CG；供 catalogue working draft 1（2026-10-29）的 testing 维度参考，后续修订可变。
- 身份：Xinghua Zhao（Independent researcher, individual capacity），ORCID 0009-0001-0512-1237。GitHub 项目身份发布于本仓。
- AI disclosure: drafted with AI assistance; every figure cited is traced to a list message the maintainer read; the reading and the position are the maintainer's.

---

## 1. The six steps

| # | Step | What it tests | Positive (must PASS) | Negative control (must FAIL) | LGD law | Discussed in thread as |
|---|------|--------------|----------------------|------------------------------|---------|------------------------|
| 1 | Create | a written record carries identity that survives time: named owner, explicit revision identity, approval | `scenarios/s1_create.example.yaml` | `s1_create.no_revision_identity.yaml` | LGD-I | the use case's identity-over-time leg |
| 2 | Modify | every change is attributable and the prior value recoverable (authority named) | `scenarios/s2_modify.example.yaml` | `s2_modify.unattributed_change.yaml` | LGD-I | correction traceability |
| 3 | History restore | a prior revision can actually be restored and its content verified against a stored digest | `scenarios/s3_restore.example.yaml` | `s3_restore.prior_unrecoverable.yaml` | LGD-II | rollback_replay column |
| 4 | Tamper detection (at rest) | integrity is verified **at rest**, not only at the front door | `scenarios/s4_tamper.example.yaml` | `s4_tamper.write_time_only.yaml` | LGD-II | the "measured at rest" reading (2026Oct/0045) |
| 5 | Retention period verification | the keeping obligation has a computable boundary and serving respects it | `scenarios/s5_period.example.yaml` | `s5_period.served_past_expiry.yaml` | LGD-III | the retention legs (MDR 10(8) / QMSR) |
| 6 | Erase vs. retain conflict | an erasure request meeting a retention obligation produces a documented resolution, not silence | `scenarios/s6_erase.example.yaml` | `s6_erase.conflict_unhandled.yaml` | LGD-III | erase_resurrect breakdown (2026Oct/0045) |

## 2. Why these six

They are the six failure surfaces that appear when catalogue item 6's question
("is the record served years later the record written on the day, and where
does the keeping/erasure boundary fall?") is operationalised:

1–2 ask **who wrote what and who changed it** (identity over time);
3–4 ask **is the content still that content** (history and at-rest integrity);
5–6 ask **may it still be kept** (the boundary: period expiry and the
erasure/retention conflict).

The public scorecard discussion in this CG (30 memory products; the
`rollback_replay` column with 13 accepted / 11 reported / 6 rejected / 9 n/a;
tamper verdicts measured at rest for only 1 of 8 rows without one; 14 rows
whose adapter has no erasure hook) is independent evidence that steps 3, 4 and
6 are exactly where implementations fail today — see 2026Oct/0045 (the
author's confirmation of the denominators and the n/a reading) in the provenance
list below. This pack does not restate those figures as measurements of any
product; it uses them only as motivation for which steps need falsifiable
tests first.

## 3. Scope and honest limits

- **Skeleton, not a product test suite.** Each step has one worked instance
  (synthetic, medical-device flavoured, consistent with the item 6 record) and
  one negative control. The complete instance must PASS; the control must FAIL,
  so a reviewer (human or AI) can confirm the check is real and falsifiable.
- The scenario records are **worked examples**, not measurements of any
  implementation. An implementation-level pack would map each step onto real
  stores via adapters (the scorecard's approach is one such mapping).
- Legal regimes cited (MDR 2017/745 Art. 10(8); 21 CFR Part 820 incorporating
  ISO 13485 Cl. 4.2.5; GDPR Art. 17) are traced to primary official sources in
  [`retention/legal_sources.md`](../retention/legal_sources.md). These vectors
  make record fields machine-checkable; they do not assert that any regime is
  legally true, and they are not legal or regulatory advice.
- These six steps are **not** defined by any agreed CG specification; they are
  the author's proposed operationalisation of catalogue item 6.

## 4. How to verify

Requires Python 3 and PyYAML (`pip install pyyaml`). Exit code 0 = PASS, 1 = FAIL.

```bash
# one-shot: run every positive (expect PASS) and every negative control
# (expect FAIL); exits 0 only if every scenario behaves as documented
python retention_pack/check_pack.py --selftest

# individual scenarios behave like the single-vector checker:
python retention_pack/check_pack.py retention_pack/scenarios/s1_create.example.yaml   # expect exit 0
python retention_pack/check_pack.py retention_pack/scenarios/s1_create.no_revision_identity.yaml  # expect exit 1
```

## 5. Provenance (all links anonymous-reachable)

- Catalogue item 6, the use case: `public-ai-agent-memory-interop` 2026Oct/0027 —
  https://lists.w3.org/Archives/Public/public-ai-agent-memory-interop/2026Oct/0027.html
- Use-case catalogue, working draft 1 (Russell Jackson, 2026-10-29): 2026Oct/0071 —
  https://lists.w3.org/Archives/Public/public-ai-agent-memory-interop/2026Oct/0071.html
- Catalogue review replies: 2026Nov/0000, 2026Nov/0004 —
  https://lists.w3.org/Archives/Public/public-ai-agent-memory-interop/2026Nov/0000.html ,
  https://lists.w3.org/Archives/Public/public-ai-agent-memory-interop/2026Nov/0004.html
- Scorecard denominators and the at-rest / n/a reading, with the author's
  confirmation of this author's corrections: 2026Oct/0045 —
  https://lists.w3.org/Archives/Public/public-ai-agent-memory-interop/2026Oct/0045.html
- Single-vector precedent in this repo: [`retention/`](../retention/) (13 checks,
  2 negative controls).

## 已核实来源

| # | 来源 | 核实的事实 | 核实日期 | 访问方式 |
|---|------|-----------|---------|---------|
| 1 | 2026Oct/0027（lists.w3.org 公开归档） | 我方 retention 用例原文（catalogue item 6 投递） | 2026-11-05 | 匿名 HTTP GET 200 |
| 2 | 2026Oct/0071（同上） | Use-case catalogue working draft 1（Russell Jackson, 2026-10-29）发布 | 2026-11-05 | 匿名 HTTP GET 200 |
| 3 | 2026Nov/0000、2026Nov/0004（同上） | 目录草案收到的审阅回复（Yasha 11-02、Russell 11-03） | 2026-11-05 | 匿名 HTTP GET 200 |
| 4 | 2026Oct/0045（同上） | scorecard 作者逐条确认我方修正（denominators、n/a 读取、at-rest 口径、erase_resurrect 拆解）；message-id tech4biz.io | 2026-11-05 | 匿名 HTTP GET 200 |
| 5 | 本仓 `retention/`（github.com 匿名 API） | 单向量先例：13 检查 + 2 负对照，checker 风格与法律引用源 | 2026-11-05 | 匿名 API GET 200 |

## 待核实 / 模型推断项

- scorecard 的宿主仓（`results/scorecard.json at c0d053f`）在 0043–0048 邮件正文中**未以 URL 形式出现**，本 PACK 因此只引列表消息、不引该仓链接——等作者 -03 修订发布或明示仓址后再补。
- 六步划分是**作者提出的操作化**（源自 ChatGPT 交叉裁定采纳项 + 我方 conformance pack 计划），CG 内尚无公认步数划分；若目录评审提出其他划分，以目录为准。
- 负对照均为结构级（缺字段/缺验证方式），不是对真实产品缺陷的复现。

## 术语与缩写

| 术语 | 含义 |
|------|------|
| LGD 三律 | LGD-I 身份（谁写的、谁改的）/ LGD-II 证据（内容仍否是原内容）/ LGD-III 治理（还可否保留）——checker 行前缀 |
| CG | W3C Community Group，此处指 AIMI CG（public-ai-agent-memory-interop） |
| catalogue item 6 | AIMI CG 用例目录第 6 条 Retention（Xinghua, 22 October） |
| at rest | 静态（存储中）完整性验证，与写入时（front door / write-time）验证相对 |
| n/a | scorecard 中"该编辑未被评估"的记法，**永远不等于通过** |
| MDR / QMSR / GDPR | 欧盟医疗器械法规 2017/745 / 美国 21 CFR Part 820（并入 ISO 13485）/ 通用数据保护条例；法源见 `retention/legal_sources.md` |
