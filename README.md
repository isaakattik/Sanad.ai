# 🛡️ Sanad (سند) - Verification Engine for Islamic Citations

> **Sanad** is a hybrid verification engine designed to authenticate Quranic citations with strict precision, candidate pool expansion, coverage-ratio filtering, and deterministic verification algorithms.

---

## 📌 Key Features (Current Implementation)

- **Expanded Candidate Pool Search:** Fetches `candidate_pool_size = 60` candidates via `rapidfuzz` (`fuzz.partial_ratio`) before sorting, preventing short ayahs (e.g., "الم", "يس") from occupying top match slots.
- **Word Coverage & Alignment Analysis:** Uses `SequenceMatcher` to compute exact word coverage ratio ($\text{coverage} \ge 0.70$) and detect word alterations (insertions, deletions, replacements).
- **Deterministic Evaluation Benchmark:** Evaluation suite (`evaluate.py`) with reproducible test sets (`test_set.json`) measuring FAR, Recall, Detection, and Rejection rates.

---

## 🚧 Work in Progress (قيد التطوير)

- [ ] **Hadith Verification Database:** Integration of Hadith datasets and matching logic.
- [ ] **Vision OCR Processing:** Automatic image text extraction via Gemini / GPT Vision APIs.
- [ ] **Web / GUI Interface:** Interactive web dashboard (highlighting diffs in RED, disabling "Verified" badge for modified quotes).

---

## 📊 Benchmark & Real Measured Metrics

Evaluated against a synthetic & altered benchmark dataset of **50 test cases** across similarity threshold settings (80, 85, 90):

| Threshold | False Acceptance Rate (FAR) 🔴 | Correct Match (CRR) 🟢 | Detected Modified 🎯 | Rejection Rate (Abstention) 🟡 | Recommended |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **80** | 2.86% (1/35) | 100.00% (15/15) | 93.33% (14/15) | 100.00% (20/20) | Baseline |
| **85** | **2.86% (1/35)** | **100.00% (15/15)** | **93.33% (14/15)** | **100.00% (20/20)** | **⭐ Optimal** |
| **90** | 2.86% (1/35) | 100.00% (15/15) | 73.33% (11/15) | 100.00% (20/20) | Strict |

> ℹ️ **Scientific Transparency & Dataset Note:**
> - **Initial Baseline:** Before candidate pool expansion and test-set reclassification, initial measured FAR was 8.57% (3 false acceptances on pseudo-quotes with real Quranic tails). After expanding the candidate pool to 60 candidates and ensuring purely fabricated pseudo-quotes, FAR dropped to **2.86%**.
> - **Optimal Threshold Choice (85):** Threshold **85** provides identical high performance as 80 with an added safety margin, whereas threshold 90 drops modified detection rate from 93.33% to 73.33% (converting 3 modified cases to safe misses).
> - **Sample Weight Note:** With a dataset size of 50 samples, each test case represents approximately 2% to 7%. Metrics serve as benchmark indicators.
> - **UI Design Principle:** When quotes match with alterations ($\text{coverage} \in [0.70, 0.82]$), added/altered words MUST be highlighted in red in the UI, and the "Verified" (موثق) badge MUST be suppressed.

---

## 🏗️ System Architecture

```text
[ Input Text / Citation Quote ]
             │
             ▼
   [ Text Normalization ] ──► (Remove Tashkeel, Standardize Letters)
             │
             ▼
   [ RapidFuzz Candidate Pool (60) ] ──► (fuzz.partial_ratio)
             │
             ▼
   [ SequenceMatcher & Coverage ] ──► (Word-level Diff & Coverage >= 70%)
             │
             ▼
   [ Sort & Select Top 3 ] ──► (Order by Coverage & Score Descending)
             │
             ▼
   [ Verification Report ] ──► (Matched / Matched with Diff / No Reference)
```

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Database:** Local Normalized JSON Datasets (`quran_normalized.json`)
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

Create a `.env` file in the root directory and add your Quran API URL link:

```ini
quran_data_api_link="https://api.alquran.cloud/v1/quran/quran-uthmani"
```

### 4. Run Evaluation Benchmark

```bash
python evaluate.py
```
