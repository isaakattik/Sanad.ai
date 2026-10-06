# 🛡️ Sanad (سند) - Verification Engine for Islamic Citations

> **Sanad** is a hybrid verification engine designed to authenticate Quranic and Hadith citations with strict precision, candidate pool expansion, sliding-window search, coverage-ratio filtering, and deterministic diff-alignment algorithms.

---

## 📌 Key Features (Current Implementation)

- **Quranic & Hadith Verification Pipelines:** Verifies both Quranic ayahs and Hadith texts while preserving full original texts (`text` and `norma_text`) rather than truncating to matn-only, maintaining full contextual integrity.
- **Sliding-Window Retrieval for Hadith:** Uses a sliding-window index (`WINDOW_SIZE = 30`, `WINDOW_STEP = 15`) coupled with query word truncation (`max_query_words = 50`) to accelerate fuzzy matching without losing alignment precision.
- **Expanded Candidate Pool Search:** Fetches `candidate_pool_size = 60` candidates via `rapidfuzz` (`fuzz.partial_ratio`) before re-ranking, preventing short ayahs (e.g., "الم", "يس") from clogging top match slots.
- **Word Coverage & Alignment Analysis:** Employs `SequenceMatcher` to compute exact word coverage ratios ($\text{coverage} \ge 0.70$) and detect fine-grained word alterations (insertions, deletions, replacements).
- **Deterministic Evaluation Benchmark:** Evaluation suite (`evaluate.py`) with reproducible test sets measuring False Acceptance Rate (FAR), Recall, Detection, Abstention, and Latency.

---

## 📢 Scientific Transparency & Dataset Disclosures

1. **Test Set Purity & Retest Protocol:**
   - Initial optimization cycles evaluated test cases prior to strict dataset splitting. Key engine mechanics (sliding windows, tail handling, and fast-path routing) were refined based on error patterns observed during early runs.
   - To ensure absolute empirical purity going forward, once engine parameters are frozen, a fresh evaluation dataset will be generated using an unexposed seed (e.g., `--seed 7`). The `--test-set` CLI parameter in `evaluate.py` enables single-pass evaluation on new external test suites.
2. **Small Class Sample Sizes:**
   - Minority classes such as `hadith_outside_scope` ($N=2$) and `popular_unsourced` ($N=2$) in the tuning set contain insufficient samples to draw broad statistical generalizations.
3. **Scholarship & Review:**
   - 4 specific Hadith edge cases remain pending formal review by an Islamic Hadith scholar to confirm their canonical grounding and classification.
4. **Latency Bottleneck Analysis:**
   - Mean latency is **1.02s** (median **0.80s**). The primary latency bottlenecks occur when querying full/plain Quranic ayahs (peaking at **4.45s** on case #3 and **3.72s** on case #12). Optimization of `find_fuzzy` for long Quranic strings remains a priority.
5. **UI & Verification Badging Principles:**
   - When citations match with modifications ($\text{coverage} \in [0.70, 0.82]$), inserted or substituted words **must** be highlighted in red, and the official "Verified" (موثق) badge **must** be suppressed in the UI.

---

## 📊 Benchmark & Real Measured Metrics

Evaluated on the **Tuning Split (`tune`)** at **Threshold = 85** across **58 cases**:

### Key Metric Summary

| Metric | Measured Value | Sample Size | 95% Confidence Interval | Target Standard |
| :--- | :---: | :---: | :---: | :--- |
| **False-Acceptance Rate (FAR)** 🔴 | **0.0%** | 0/31 | 0.0% – 11.0% | Lower is better |
| ↳ *Tampered returned as exact* | **0.0%** | 0/17 | 0.0% – 18.0% | 0% Target |
| ↳ *Not-in-books accepted* | **0.0%** | 0/14 | 0.0% – 22.0% | 0% Target |
| **Quran Recognition Accuracy** 🟢 | **100.0%** | 9/9 | 70.0% – 100.0% | High Precision |
| **Hadith Recognition Accuracy** 🟢 | **100.0%** | 15/15 | 80.0% – 100.0% | High Precision |
| **Tampered Quotes Detected** 🎯 | **94.1%** | 16/17 | 73.0% – 99.0% | High Recall |
| ↳ *Quran Tampered Detected* | **90.9%** | 10/11 | 62.0% – 98.0% | — |
| ↳ *Hadith Tampered Detected* | **100.0%** | 6/6 | 61.0% – 100.0% | — |
| **Tampered Safely Refused** 🛡️ | **5.9%** | 1/17 | 1.0% – 27.0% | Safe Miss |
| **Abstention Rate (Not in books)** 🟡 | **100.0%** | 14/14 | 78.0% – 100.0% | Complete Rejection |
| **Too-Short Input Guard** 🛑 | **100.0%** | 3/3 | 44.0% – 100.0% | Early Guardrail |
| **Source Accuracy (Quran/Hadith)** 🧭 | **98.3%** | 57/58 | 91.0% – 100.0% | High Classification |
| **Returned Reference == Origin** 📍 | **94.3%** | 33/35 | 81.0% – 98.0% | Informational |

### Performance & Query Latency

- **Mean Latency:** `1.02s`
- **Median Latency:** `0.80s`
- **95th Percentile (p95):** `3.43s`
- **Max Latency:** `4.45s` (*Slowest cases: #3 correct_quran_full 4.45s \| #12 correct_quran_plain 3.72s \| #4 correct_quran_full 3.43s*)

---

## 🗂️ Category Outcome Breakdown

| Category | Outcomes Count | Status |
| :--- | :--- | :---: |
| `correct_quran_full` | `correct=3` | 🟢 Passed |
| `correct_quran_partial` | `correct=3` | 🟢 Passed |
| `correct_quran_plain` | `correct=3` | 🟢 Passed |
| `modified_quran` | `detected=7`, `safe_miss=1` | 🎯 Detected / Safe Refusal |
| `extended_quran` | `detected=3` | 🎯 Detected |
| `correct_hadith` | `correct=6` | 🟢 Passed |
| `correct_hadith_plain` | `correct=2` | 🟢 Passed |
| `long_hadith` | `correct=2` | 🟢 Passed |
| `modified_hadith` | `detected=6` | 🎯 Detected |
| `famous_hadith` | `correct=5` | 🟢 Passed |
| `famous_too_short` | `guard_ok=1` | 🛑 Guardrail OK |
| `hadith_outside_scope` | `rejected=2` | 🟡 Rejected |
| `popular_unsourced` | `rejected=2` | 🟡 Rejected |
| `pseudo_quran` | `rejected=5` | 🟡 Rejected |
| `general_fabricated` | `rejected=5` | 🟡 Rejected |
| `short_input` | `guard_ok=2` | 🛑 Guardrail OK |

---

## 🚧 Work in Progress & Roadmap

- [x] **Hadith Verification Database:** Integrated sliding-window indexing and rapid fuzzy retrieval for Hadith datasets.
- [x] **Zero FAR & High Recall Thresholding:** Achieved 0.0% FAR and 94.1% tampered detection at threshold 85.
- [ ] **Quran Search Optimization:** Accelerating `find_fuzzy` for long Quranic ayahs to reduce p95 latency below 1.5s.
- [ ] **Vision OCR Processing:** Automatic image-based citation extraction via Gemini / GPT Vision APIs.
- [ ] **Interactive Web Dashboard:** Modern Web GUI with inline diff rendering (highlighting alterations in RED) and conditional badge suppression.

---

## 🏗️ System Architecture

```text
               [ Input Citation Quote ]
                          │
                          ▼
              [ Text Normalization ]
    (Strip Tashkeel, Normalize Alef/Yaa/Taa)
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
  [ Quran Fuzzy Pool ]        [ Hadith Window Pool ]
(Candidate Pool Size = 60)   (Sliding Windows + Query Limit)
            │                           │
            └─────────────┬─────────────┘
                          ▼
            [ SequenceMatcher & Diff Engine ]
            (Word-level Diffs & Coverage >= 70%)
                          │
                          ▼
            [ Candidate Ranking & Selection ]
            (Sorted by Coverage & Fuzzy Score)
                          │
                          ▼
              [ Verification Report ]
       (Matched / Matched_with_Diff / No_Reference)
```

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Databases:** Local Normalized JSON Datasets (`quran_normalized.json`, `hadith_normalized.json`)
- **Core Libraries:** `rapidfuzz`, `difflib` (`SequenceMatcher`), `requests`, `python-dotenv`

---

## 🚀 Getting Started

### 1. Clone the Repository & Setup Environment

```bash
git clone https://github.com/isaakattik/Sanad.ai.git
cd Sanad.ai
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables Setup

Create a `.env` file in the root directory and configure the data endpoint:

```ini
quran_data_api_link="https://api.alquran.cloud/v1/quran/quran-uthmani"
```

### 4. Run Evaluation Benchmark

Run standard evaluation on the tuning set:

```bash
python evaluate.py --split tune --threshold 85
```

Run evaluation with detailed case-by-case outcome outputs:

```bash
python evaluate.py --split tune --threshold 85 --details
```

Run evaluation on a fresh test set using a custom path:

```bash
python evaluate.py --test-set test_suite_seed7.json
```