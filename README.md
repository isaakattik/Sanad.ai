# 🛡️ Sanad (سند) - Verification Engine for Islamic Citations

> **Sanad** is a hybrid verification engine designed to authenticate Quranic and Hadith citations with strict precision, candidate pool expansion, sliding-window search, coverage-ratio filtering, and deterministic diff-alignment algorithms.

---

## 📌 Key Features (Current Implementation)

- **Quranic & Hadith Verification Pipelines:** Verifies both Quranic ayahs and Hadith texts while preserving full original texts (`text` and `norma_text`) rather than truncating to matn-only, maintaining full contextual integrity.
- **Sliding-Window Retrieval for Hadith:** Uses a sliding-window index (`WINDOW_SIZE = 30`, `WINDOW_STEP = 15`) coupled with query word truncation (`max_query_words = 50`) to accelerate fuzzy matching without losing alignment precision.
- **Expanded Candidate Pool Search:** Fetches `candidate_pool_size = 60` candidates via `rapidfuzz` (`fuzz.partial_ratio`) before re-ranking, preventing short ayahs (e.g., "الم", "يس") from clogging top match slots.
- **Word Coverage & Alignment Analysis:** Employs `SequenceMatcher` to compute exact word coverage ratios ($\text{coverage} \ge 0.70$) and detect fine-grained word alterations (insertions, deletions, replacements).
- **Deterministic Evaluation Benchmark:** Evaluation suite (`evaluate.py`) with reproducible test sets (`test_set.json`) measuring False Acceptance Rate (FAR), Recall, Detection, and Rejection rates.

---

## 📢 Scientific Transparency & Dataset Disclosures

1. **Test Set Purity & Retest Protocol:**
   - Initial optimization cycles evaluated all 106 benchmark cases prior to strict dataset splitting. Algorithms (sliding windows, tail handling, and fast-path routing) were refined based on error patterns observed during these early runs.
   - To ensure absolute empirical purity, once the engine parameters and thresholds are frozen, a fresh evaluation dataset will be generated using an unexposed seed (e.g., `--seed 7`). The `--test-set` CLI parameter in `evaluate.py` enables single-pass evaluation on new external test suites.
2. **Small Class Sample Sizes:**
   - Minority classes such as `hadith_outside_scope` ($N=2$) and `popular_unsourced` ($N=2$) in the tuning set contain insufficient samples to draw statistical generalizations.
3. **Scholarship & Review:**
   - 4 specific Hadith edge cases remain pending formal review by an Islamic Hadith scholar to confirm their canonical grounding and classification.
4. **Latency Bottleneck Analysis:**
   - While Hadith search latency was successfully reduced from 17.0s down to ~0.9s via sliding windows and query capping, the current primary latency bottleneck occurs in `find_fuzzy` when querying long Quranic ayahs (peaking at ~4.45s). Optimization of `find_fuzzy` is prioritized for the next release.
5. **UI & Verification Badging Principles:**
   - When citations match with modifications ($\text{coverage} \in [0.70, 0.82]$), inserted or substituted words **must** be highlighted in red, and the official "Verified" (موثق) badge **must** be suppressed in the UI.

---

## 🚧 Work in Progress & Roadmap

- [x] **Hadith Verification Database:** Integrated sliding-window indexing and rapid fuzzy retrieval for Hadith datasets.
- [ ] **Quran Search Optimization:** Accelerating `find_fuzzy` for long ayahs to reduce peak query latency.
- [ ] **Vision OCR Processing:** Automatic image-based citation extraction via Gemini / GPT Vision APIs.
- [ ] **Interactive Web Dashboard:** Modern Web GUI with inline diff rendering (highlighting alterations in RED) and conditional badge suppression.

---

## 📊 Benchmark & Real Measured Metrics

Evaluated against a benchmark dataset of test cases across similarity threshold settings (80, 85, 90):

| Threshold | False Acceptance Rate (FAR) 🔴 | Correct Match (CRR) 🟢 | Detected Modified 🎯 | Rejection Rate (Abstention) 🟡 | Recommended |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **80** | 2.86% (1/35) | 100.00% (15/15) | 93.33% (14/15) | 100.00% (20/20) | Baseline |
| **85** | **2.86% (1/35)** | **100.00% (15/15)** | **93.33% (14/15)** | **100.00% (20/20)** | **⭐ Optimal** |
| **90** | 2.86% (1/35) | 100.00% (15/15) | 73.33% (11/15) | 100.00% (20/20) | Strict |

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

Run the standard evaluation benchmark:

```bash
python evaluate.py
```

Run evaluation on a fresh test set using a custom path:

```bash
python evaluate.py --test-set test_suite_seed7.json
```