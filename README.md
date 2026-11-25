# WorkLedger — Reproduction Package

**Companion to** *WorkLedger: An Auditable Instrument for Measuring Work Output in AI-Augmented Organizations*  
Stage 1 proposal, *Organization Science*, Special Issue on AI-Enabled Frontiers in Organizational Science

Version 1.0 · 25 November 2026

---

## 1. Purpose

The two technical documents in this deposit make a specific kind of claim: that this many turns, this many  
words, this many objects, these exact quotations, and these exact timestamps. Every one of those claims can be  
recomputed from the deposited files — without the software, without a language model, and without access to  
the firm.

This package makes that recomputation available to the editor and reviewers in a single command:

```
cd WorkLedger_Reproduction
python3 verify_all.py
```

Ten checks run in under a second. They are deliberately mechanical: none asks the reader to accept an  
interpretation. Each returns a number that can be compared with a number printed in the documents.

Two points of orientation, so that the run is not misread in either direction:

- **This is not the software.** The worked example in the demo report was coded by hand, and the report says  
  so in its first paragraph. A passing run does not show that the pipeline extracts correctly. It shows that  
  the hand coding is internally consistent and faithful to the transcript it cites. §7 states precisely where  
  this boundary lies.
- **A difference is reported, not absorbed.** Where a figure in the documents and the same figure recomputed  
  from the files do not agree, the script prints both and moves on. Two such cases occur in this deposit; they  
  are small, they are confined to how a count is stated rather than to what the documents argue, and they are  
  set out in §6.

**Summary of this run:** seven checks pass, two report a difference, one is informational.  
`C1`, `C2`, `C3`, `C5`, `C6`, `C8`, `C9` pass. The differences reported by `C7` and `C4` are explained in §6.1  
and §6.2. `C10` is informational because an auxiliary file is not part of this deposit (§8).

---

## 2. Contents

| Path                        | What it is                                                                      |
| --------------------------- | ------------------------------------------------------------------------------- |
| `README.md`                 | this document                                                                   |
| `verify_all.py`             | the verifier; Python standard library only, no dependencies                     |
| `WorkLedger.md`             | technical appendix: purpose, entity scheme, competency questions, stated limits |
| `WorkLedger_demo_report.md` | worked example on interview INT-03, with three sample records                   |
| `transcripts/`              | field appendix: four interviews, a reader's note, a thematic index              |

The six files in `transcripts/` are byte-identical to the appendix in the submission. Hashes are recorded here  
so that any citation to a timestamp can be tied to one specific text.

**Table 1. Transcript manifest**

| File                     | SHA-256                                                            |
| ------------------------ | ------------------------------------------------------------------ |
| `00_README.md`           | `5f9f284c75ba0a3c8083533b3d2a93b9ce8dcd0891c12faf276578826ad8db18` |
| `01_interview_INT-01.md` | `1cbf4ad5425ecf346f91a824a38042a96e768cee7f09c568c2983dc0685a0eff` |
| `02_interview_INT-02.md` | `09c6838331bfb136be15cc4c96e1e181d408c627dd11781ef1f481b4830e3f22` |
| `03_interview_INT-03.md` | `aab53eecaae00a2b849e017141d78a83f8d12b5433954c67030941b9354d577e` |
| `04_interview_INT-04.md` | `10d0c1f37818ff2d9a6ca4496d2410475241d506f6b6c30adaaf5c42874840d6` |
| `99_index.md`            | `2d4ae04f4858a1288ba5206a1715e2dfbd549560fb54801696a84b41c1650c2b` |

The appendix as submitted (`Partner Company CEO_Interviews_Appendix.zip`, 75,752 bytes,  
`05af7fba720d73a7590d6328826b48394d7aad563e4018df3e9b9aeefda65245`) contains these six files and nothing else.

---

## 3. Requirements

Python 3.6 or later. Nothing else — no packages, no virtual environment, no network access, no credentials, no  
access to the firm. On Windows, use `python` where the examples say `python3`.

The script reads only the files listed above. It writes nothing to disk and contacts no server.

---

## 4. Running the verifier

From this folder, against the transcripts included here:

```
python3 verify_all.py
```

Against the submitted zip instead:

```
python3 verify_all.py "../Partner Company CEO_Interviews_Appendix.zip"
```

Against the combined single-file appendix:

```
python3 verify_all.py "../Partner Company CEO_Interviews_Appendix_combined.md"
```

Either input is accepted; the second line of output states which one was used. Runtime is under a second,  
most of it interpreter startup. Exit code is `0` when every check either passes or reports a difference  
explained in §6, and `1` when an unexplained difference appears.

**Expected output** (folder input; the zip produces the same lines under a different `source:` label):

```text
WorkLedger reproduction package -- verification
source: transcripts/
------------------------------------------------------------------------------
C1   deposit integrity (sha256)         PASS  6 files, sha256 as recorded in README table 1
C2   turn and section census            PASS  INT-01 320 turns (R1 192 / R2 80 / R3 48), 12
                                              sections; INT-02 235 turns (R1 120 / R2 64 / R3 19 /
                                              R4 23 / R5 9), 19 sections; INT-03 30 turns (R1 18 /
                                              R2 7 / R3 5), 4 sections; INT-04 31 turns (R1 16 /
                                              R2 5 / R3 10), 5 sections
C3   word census vs appendix table      PASS  wc -w within 1% of the appendix table: INT-01 19042
                                              vs 19000 (0.22%); INT-02 9758 vs 9750 (0.08%);
                                              INT-03 1760 vs 1750 (0.57%); INT-04 1350 vs 1350
                                              (0.00%) | demo report states 1,756, file counts 1760
                                              (0.23%)
C4   duration vs last timestamp         DIFF  INT-03 header says 12 min, last turn at 10:10;
                                              INT-04 header says 8 min, last turn at 06:40 |
                                              measured: INT-01 117 vs 117.5; INT-02 60 vs 60.1;
                                              INT-03 12 vs 10.2; INT-04 8 vs 6.7
C5   quotation fidelity                 PASS  6 quotations resolve to the cited turn and speaker
C6   evidence identifiers resolve       PASS  3 evidence identifiers resolve to a turn with the
                                              stated speaker
C7   ledger arithmetic                  DIFF  table sums to 48 objects (49 with the coverage
                                              report); the report states twenty-nine and 35
                                              (README 6.1)
C8   the instrument's prohibitions hold PASS  no scalar score, derivation withheld, no Evaluation
                                              object
C9   index locators resolve             PASS  32 index locators resolve to a section and a real
                                              turn
C10  record-level checks (optional)     INFO  demo_objects.jsonl not in this copy -- record-level
                                              checks skipped
------------------------------------------------------------------------------
10 checks: 7 passed, 2 reported a difference, 1 informational
Each reported difference is explained in README.md section 6.
```

---

## 5. The ten checks

| ID  | Claim under test                                                               | How it is tested                                                                                    | Result here                   |
| --- | ------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------- | ----------------------------- |
| C1  | The transcripts are the ones the appendix describes                            | SHA-256 against Table 1                                                                             | pass, six of six              |
| C2  | INT-03 has 30 speaker turns; the four files have 12 / 19 / 4 / 5 sections      | Turn labels `**R# (mm:ss)**` and section headings counted per file                                  | pass                          |
| C3  | The word counts in the appendix table are honest                               | Whitespace tokens per file, 1% tolerance                                                            | pass, all four within 0.6%    |
| C4  | A declared duration matches the record                                         | `Duration: approx. N minutes` against the last timestamp                                            | difference on two files, §6.2 |
| C5  | Every quotation attributed to INT-03 is present, at that turn, by that speaker | Case-folded substring match inside the labelled turn                                                | pass, six of six              |
| C6  | Evidence identifiers such as `INT-03:06:07:R1` point at real turns             | Regex extraction, then lookup of the speaker at that timestamp                                      | pass, three of three          |
| C7  | The ledger's stratum counts add up                                             | §1 table parsed and summed, compared with the totals in the prose                                   | difference, §6.1              |
| C8  | The samples obey the instrument's own prohibitions                             | No scalar score emitted; derivation carries a withheld gate; no Evaluation object on interview data | pass, three of three          |
| C9  | The thematic index locators are usable                                         | `INT-0n §k, mm:ss` parsed; section exists; cited moment is a turn                                   | pass, 32 of 32                |
| C10 | If present, `demo_objects.jsonl` matches the report and the schema             | JSON Lines parsed; object types, verdict vocabulary, evidence on every *supported*                  | informational, §8             |

Three constants at the top of `verify_all.py` — `DECLARED`, `DEMO_STRATA`, `QUOTES` — transcribe what the  
appendix and the report assert. A reader who disagrees with a count can edit one of them and re-run; the checks  
then test the reader's version instead of the deposited one. That is the intended use, and the demo report's §6  
invites it.

---

## 6. Notes on counts and conventions

Three figures in the deposit invite a question from a reader who counts. None affects a finding; all three are  
recorded here so the script's output reads unambiguously.

### 6.1 Record totals (C7)

The §1 table of the demo report lists 30 source fragments, 17 claims, no facts, no evaluations, and one derived  
assessment — **48 records**, or **49** including the coverage report named in §6. Two sentences of prose state  
other totals ("twenty-nine records out"; "all 35 records"). The table is the operative count; the two sentences  
are being corrected in the revision of the manuscript.

What the worked example establishes does not depend on the total: an empty fact stratum, an empty evaluation  
stratum, and seventeen claims each adjudicated insufficient evidence. Those are the figures the argument rests  
on, and the table already gives them.

### 6.2 Stated interview duration (C4)

`03_interview_INT-03.md` opens with approximately 12 minutes; its last turn is at 10:10 and the appendix table  
gives 10. `04_interview_INT-04.md` opens with approximately 8 minutes; its last turn is at 06:40 and the table  
gives 7. INT-01 and INT-02 agree with their records to within half a minute.


Citations in both documents are always to a timestamp — 06:07, 01:18, 07:48 — and never to a stated duration,  
so no evidence claim depends on the header. Where a duration is quoted from this deposit, the figures  
consistent with the record are **10 minutes** and **7 minutes**.

### 6.3 Word counts are a convention, not a measurement (C3)

The demo report says 1,756 words for INT-03; `wc -w` on the deposited file gives 1,760, a difference of 0.23%.  
The count is whitespace tokens over the whole file, including headings and speaker labels. Counting only spoken  
words, excluding headings and labels, gives 1,335. Each figure is correct under a stated rule, which is why the  
check applies a 1% tolerance and prints the rule rather than asserting one number.

If a single figure is required: **1,760 words in the file, 1,335 of them spoken, across 30 turns.** The  
appendix table's 1,750 is a round figure of the same quantity.

---

## 7. What a successful run establishes, and what it does not

The run establishes four things, and they are the four a reviewer of a Stage 1 proposal is in a position to  
test without having to trust the implementation:

1. The deposited transcripts are the ones the appendix describes, byte for byte.
2. Every count asserted in the appendix table is recoverable from the files.
3. Every quotation and every `speaker · interview · timestamp` identifier resolves to the turn it names.
4. The sample records in the demo report obey the instrument's own prohibitions.

It does not establish the following, and no re-run can:

- **The claim inventory.** That there are seventeen claims, and that these are the claims, is a hand coding  
  against the entity scheme in `WorkLedger.md`. A second coder would plausibly arrive at fifteen or nineteen.  
  The demo report states that this is a hand coding; the package does not claim more.
- **Which utterances are evaluative.** The count of four is a reading of tone, and the threshold is not defined  
  in the deposit. C8 therefore tests only the structural claim that no utterance was promoted to an Evaluation  
  object, not the semantic one.
- **The capability derivation.** The definition, the `0.1-draft` label, the confidence of 0.24, and the expiry  
  date are supplied by the coder. C10 can check that a record carries them; nothing can check that 0.24 is the  
  right number. The claim the documents make is narrower — that a value below threshold should be withheld —  
  and C8 does verify that.
- **Anything about the firm or about firms in general.** The corpus is one firm and four conversations, a  
  convenience sample. A passing run says nothing beyond what is quoted.
- **That the extraction pipeline works.** No extraction, retrieval, or model call happens here. The  
  synthetic-organisation demonstration described in the proposal is a separate deposit.

One limit is worth stating because it is the report's own finding: the fact stratum is empty *for this corpus*.  
C7 confirms the zero; it cannot confirm the interpretation that interview talk yields claims about work rather  
than records of it. That inference rests on the argument in §3 of the demo report, and is for readers to judge.

---

## 8. The record-level file (C10)

The demo report's §6 refers to `demo_objects.jsonl`, which holds the individual records. That file is not part  
of this deposit, so C10 reports `INFO` and stops rather than failing.

If the file is placed beside `verify_all.py`, C10 runs and checks four properties: every line parses as JSON;  
every object is one of the six declared types; every Claim carries a verdict from the four-value vocabulary,  
and none is marked *supported* without at least one supporting fragment; every SourceFragment carries speaker,  
timestamp, and text. It does not check whether the claim inventory is complete or correct — see §7.

Until the file is supplied, the record-level statements in §6 of the demo report are the one part of the worked  
example that cannot be confirmed by running something. Everything else in the two documents is covered by C1–C9.

---

## 9. Confidentiality, citation, and contact

The transcripts were collected for research and are deposited for review. They contain no customer material  
and no personal names: individuals appear as R1–R5 and the firm as China Spring. They are provided to the  
editor and reviewers for the purpose of evaluating this submission and should not be redistributed further.

Quotations should carry the form used throughout the deposit — `(R1, INT-03, 06:07)` — so that a reader can  
return to the turn. When citing the package itself, cite it as a companion deposit to the proposal and give the  
version and date in the header above.

Nothing in this package should be read as an evaluation of any named person's performance, and the instrument  
is not offered as a basis for termination, promotion, or pay in its present form.

Correspondence should go through the corresponding author's institutional address as recorded in the  
submission system.

---

## 10. If you have ten minutes

1. `WorkLedger_demo_report.md` §1–§2. Two pages: the shape of the output, and three records.
2. §6 of this document. Three figures and the conventions behind them.
3. `transcripts/03_interview_INT-03.md`, the turns at 01:18, 04:35, 06:07, and 07:48. These are the four  
   moments the worked example is built on, and they read in four minutes.

`WorkLedger.md` §5 then lists the five things the instrument refuses to do, and §4 the questions it must answer  
before it counts as a model at all.
