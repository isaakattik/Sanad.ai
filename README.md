
# 🛡️ Sanad (سند) - Verification Engine for Islamic Citations

> **Sanad** is a hybrid, zero-hallucination verification system designed to authenticate Quranic verses and Hadiths in media, posters, and digital designs with strict precision and absolute data integrity.

---

## 📌 Key Features

- **Precise Quran Matching:** Local search engine featuring text normalization, exact matching, and partial phrase identification.
- **Hadith Text Alignment & Diff Analysis:** Fuzzy matching algorithms that detect text alterations, word insertion, or omission using word-level diff alignment (`ndiff`).
- **Strict Vision OCR Processing:** Image text extraction via Vision APIs with strict instructions preventing automatic spell correction or textual altering.
- **Human-in-the-Loop Architecture:** Generative AI is restricted solely to OCR extraction and classification, while validity and verification logic are handled by deterministic local algorithms.
- **Zero-Tolerance Metrics:** Evaluated against synthetic and altered datasets achieving a **False Acceptance Rate (FAR) of 0.0%**.

---

## 🏗️ System Architecture

[ Poster / Design Image ]
│
▼
[ Vision OCR API ] ──► (Literal Text Extraction & Comment Separation)
│
▼
[ Text Normalization ] ──► (Diacritics Removal, Letter Standardizing)
│
┌──────┴──────────────────────────┐
▼                                 ▼
[ Quran Verification ]     [ Hadith Verification ]
(Exact & Partial Search)   (Fuzzy Alignment & Diff)
│                                 │
└──────┬──────────────────────────┘
▼
[ Verification Report ]

---

## 🛠️ Tech Stack

- **Language:** Python 3.10+
- **Database:** Local JSON Datasets (Quran & Hadith)
- **Vision & OCR:** Gemini Vision API / GPT-4o Vision
- **Core Libraries:** `difflib` (`SequenceMatcher`, `ndiff`), `re`, `python-dotenv`

---

## 🚀 Getting Started

### 1. Clone the Repository & Setup Environment

```bash
git clone https://github.com/isaakattik/Sanad.ai.git
cd Sanad.ai
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


2. Install Dependencies

pip install -r requirements.txt

3. Environment Variables Setup
Create a .env file in the root directory and add your API credentials:

quran_data_api_link = "Your API Key here"

```

