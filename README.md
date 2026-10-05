# 🛡️ Sanad (سند) - Verification Engine for Islamic Citations

> **Sanad** is a verification system designed to authenticate Quranic verses in media, posters, and digital designs with strict precision and deterministic verification algorithms.

---

## 📌 Key Features (Current Implementation)

- **Precise & Fuzzy Quran Matching:** Fast local search engine powered by `rapidfuzz` (`fuzz.partial_ratio`) combined with text normalization.
- **Word Coverage & Alignment Analysis:** `SequenceMatcher` algorithm calculates word coverage ratio and detects word alterations (insertions, deletions, replacements).
- **Short-Ayah False Positive Prevention:** Coverage metrics ensure short ayahs (e.g., "الم", "يس") do not generate false positive 100% matches on long input texts.
- **Deterministic Evaluation Benchmark:** Evaluation suite (`evaluate.py`) with reproducible test sets (`test_set.json`) measuring FAR, Recall, and Rejection rates.

---

## 🚧 Work in Progress (قيد التطوير)

- [ ] **Hadith Verification Database:** Integration of Hadith datasets and matching logic.
- [ ] **Vision OCR Processing:** Automatic image text extraction via Gemini / GPT Vision APIs.
- [ ] **Web / GUI Interface:** Interactive web dashboard for end users.

---

## 📊 Benchmark & Real Measured Metrics

Evaluated against a synthetic & altered benchmark dataset of **50 test cases** across similarity threshold settings (80, 85, 90):

| Threshold | False Acceptance Rate (FAR) 🔴 | Correct Match (CRR) 🟢 | Detected Modified 🎯 | Rejection Rate (Abstention) 🟡 |
| :---: | :---: | :---: | :---: | :---: |
| **80** | 8.57% (3/35) | 93.33% (14/15) | 66.67% (10/15) | 85.00% (17/20) |
| **85** | 8.57% (3/35) | 93.33% (14/15) | 66.67% (10/15) | 85.00% (17/20) |
| **90** | **5.71% (2/35)** | **93.33% (14/15)** | **46.67% (7/15)** | **90.00% (18/20)** |

---

## 🏗️ System Architecture

```text
[ Input Text / Verse Quote ]
             │
             ▼
   [ Text Normalization ] ──► (Remove Tashkeel, Standardize Letters)
             │
             ▼
   [ RapidFuzz Alignment ] ──► (Partial Match Scorer)
             │
             ▼
   [ SequenceMatcher & Coverage ] ──► (Word-level Diff & Coverage >= 70%)
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
