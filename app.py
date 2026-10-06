"""app.py: Sanad web server.  Run:  uvicorn app:app --reload   (then open http://127.0.0.1:8000)"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from normalize import normalize_arabic
from Search_engin import verify_quote

STATIC = Path(__file__).parent / "static"
app = FastAPI(title="Sanad API", docs_url="/docs")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


class VerifyRequest(BaseModel):
    text: str = Field(..., max_length=3000)


def reference_label(m: dict) -> str:
    if "surah_number" in m:
        return f"{m['surah_name']} · الآية {m['ayah_number']}"
    return f"{m['source_book']} · حديث رقم {m['hadith_number']}"


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


@app.post("/api/verify")          # plain `def`: FastAPI runs it in a thread pool
def verify(req: VerifyRequest):
    res = verify_quote(req.text)
    best = res["best_match"]

    bad_words = set()             # normalized words of the user's text that differ from the source
    if best:
        best = {**best, "reference": reference_label(best)}
        for d in best["differences"]:
            bad_words.update(d["user_words"])

    tokens = []                   # the user's ORIGINAL words (with tashkeel), flagged if they differ
    for tok in req.text.split():
        norm = normalize_arabic(tok)
        tokens.append({"t": tok, "bad": bool(norm) and norm in bad_words})

    others = [{"reference": reference_label(c), "score": round(c["score"], 1),
               "status": c["match_type"]}
              for c in res["all_candidates"] if c["match_type"] != "no_reference"
              and c is not res["best_match"]][:3]

    return {"status": res["status"], "source_type": res["source_type"],
            "best_match": best, "tokens": tokens, "others": others}
