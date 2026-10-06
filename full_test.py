
import argparse
import json
import random
import re
from collections import Counter
from pathlib import Path

from normalize import normalize_arabic

DB_DIR = Path("Database")
QURAN_FILE = DB_DIR / "quran_normalized.json"
HADITH_FILE = DB_DIR / "hadith_normalized.json"
DEFAULT_OUT = DB_DIR / "test_set.json"

NAWAWI = "الأربعون النووية"
MIN_WORDS = 3   

CHAIN_MARKERS = {"حدثنا", "حدثني", "اخبرنا", "اخبرني", "انبانا", "انبأنا"}
SEP = " | " 


COUNTS = {
    "correct_quran_full": 5,      
    "correct_quran_partial": 5,   
    "correct_quran_plain": 5,     
    "modified_quran": 15,        
    "extended_quran": 5,          
    "correct_hadith": 12,         
    "correct_hadith_plain": 3,    
    "long_hadith": 3,            
    "modified_hadith": 12,        
}

# Hand-written inputs
FAMOUS_SAYINGS = [
    "إنما الأعمال بالنيات وإنما لكل امرئ ما نوى",
    "من غشنا فليس منا",
    "خيركم من تعلم القرآن وعلمه",
    "اتق الله حيثما كنت وأتبع السيئة الحسنة تمحها",
    "المسلم من سلم المسلمون من لسانه ويده",
    "الطهور شطر الإيمان والحمد لله تملأ الميزان",
    "الدين النصيحة",
    "لا يؤمن أحدكم حتى يحب لأخيه ما يحب لنفسه",
    "من كان يؤمن بالله واليوم الآخر فليقل خيرا أو ليصمت",
    "من حسن إسلام المرء تركه ما لا يعنيه",
    "بني الإسلام على خمس",
]


OUTSIDE_SCOPE_HADITH = [
    ("طلب العلم فريضة على كل مسلم ومسلمة",          "reported in Sunan, not in the Sahihayn"),
    ("إن الله يحب إذا عمل أحدكم عملا أن يتقنه",      "reported outside the Sahihayn"),
    ("اطلبوا العلم ولو في الصين",                     "reported outside the Sahihayn, weak"),
    ("النظافة من الإيمان",                            "popular wording, not in the Sahihayn"),
]


POPULAR_UNSOURCED = [
    "الدين المعاملة والصدق أمانة",
    "لا تؤخر عمل اليوم إلى الغد",
    "حب الوطن من الإيمان",
]


PSEUDO_QURANIC = [
    "وأقيموا العدل والتراحم في أسركم لعلكم تصبحون",
    "إن الله يعلم ما تسرون في قلوبكم وإليه مصيركم أجمعين",
    "يا أيها الناس اتقوا ربكم وكونوا مع الصديقين في أفعالهم",
    "ولئن ثبتتم على الحق إن ذلك من خير الأعمال للعباد",
    "وقولوا قولا سديدا وأصلحوا ذات بينكم في مساكنكم",
    "إن في تقلب الليل والنهار لعلامات لأهل النظر والتفكر",
    "وما الحياة الدنيا إلا دار الابتلاء والتمحيص للبشر",
    "فمن يفعل الطيبات وهو مؤمن فلا ضياع لجهده عند ربه",
    "سبحان الذي أبدع السموات وأنزل فيها من كل بركة",
    "واصبر على ما ينالك واصفح الصفح الجميل عن الجميع",
]


GENERAL_FABRICATED = [
    "القراءة تغذي العقل وتوسع مدارك الإنسان في الحياة",
    "الرياضة تنشط الجسم وتحافظ على الصحة السليمة",
    "التكنولوجيا الحديثة غيّرت أسلوب التواصل بين البشر",
    "العمل الجماعي يحقق النجاح والتفوق في المؤسسات",
    "التعليم هو الأساس لبناء المجتمعات المتقدمة والراقية",
    "الصبر والاجتهاد هما مفتاح النجاح في جميع المجالات",
    "الحفاظ على البيئة واجب على كل مواطن في المجتمع",
    "السفر يفتح آفاقا جديدة للتعلم واكتساب الخبرات",
    "التخطيط الجيد يساعد على إنجاز الأهداف بدقة وفاعلية",
    "احترام الآخرين يعكس أخلاق الإنسان وتربيته الحسنة",
]


TOO_SHORT = ["الحمد لله", "قل هو", "إنما الأعمال"]



# Helpers

def real_words(text: str) -> list:
    """Whitespace tokens that still contain letters after normalization.
    Drops lone punctuation, tatweel and waqf marks (e.g. '،', 'ـ', 'ۖ')."""
    return [w for w in text.split() if normalize_arabic(w)]


class Corpus:


    def __init__(self, quran: list, hadith: list):
        self.quran_blob = SEP.join(a["norma_text"] for a in quran)
        self.hadith_blob = SEP.join(h["norma_text"] for h in hadith)

    def in_quran(self, text: str) -> bool:
        n = normalize_arabic(text)
        return bool(n) and n in self.quran_blob

    def in_hadith(self, text: str) -> bool:
        n = normalize_arabic(text)
        return bool(n) and n in self.hadith_blob

    def contains(self, text: str) -> bool:
        return self.in_quran(text) or self.in_hadith(text)


def quran_origin(a: dict) -> dict:
    return {"source": "quran", "surah": a["surah_number"], "ayah": a["ayah_number"]}


def hadith_origin(h: dict) -> dict:
    return {"source": "hadith", "book": h["source"], "number": h["hadith_number"]}


def hadith_segment(item: dict) -> list:


    quoted = [real_words(m) for m in re.findall(r'"([^"]+)"', item["text"])]
    quoted = [q for q in quoted if len(q) >= 10]
    if quoted:
        return max(quoted, key=len)
    words = real_words(item["text"])
    if item["source"] == NAWAWI:
        return words
    return words[len(words) // 2:]


def has_chain(words: list) -> bool:
    return any(normalize_arabic(w) in CHAIN_MARKERS for w in words)


def pick_window(words: list, rng: random.Random, lo: int, hi: int) -> list:
    length = rng.randint(lo, min(hi, len(words)))
    start = rng.randint(0, len(words) - length)
    return words[start:start + length]


def apply_edit(words: list, kind: str, rng: random.Random, vocab: list):
    """Edit strictly inside the text (never within the first/last two words)."""
    new = list(words)
    idx = rng.randint(2, len(new) - 3)
    if kind == "delete":
        removed = new.pop(idx)
        return new, {"kind": "delete", "index": idx, "word": normalize_arabic(removed)}
    original_norm = normalize_arabic(new[idx])
    for _ in range(50):
        candidate = rng.choice(vocab)
        if normalize_arabic(candidate) != original_norm:
            break
    if kind == "replace":
        old = new[idx]
        new[idx] = candidate
        return new, {"kind": "replace", "index": idx,
                     "old": normalize_arabic(old), "new": normalize_arabic(candidate)}
    new.insert(idx, candidate)
    return new, {"kind": "insert", "index": idx, "word": normalize_arabic(candidate)}


# Generator

class Generator:
    def __init__(self, quran: list, hadith: list, seed: int):
        self.rng = random.Random(seed)
        self.quran = quran
        self.hadith = hadith
        self.corpus = Corpus(quran, hadith)
        self.cases = []
        self.used = set()      # normalized texts already used (no duplicates)
        self.rejected = Counter()

        self.q_words = [(a, real_words(a["text"])) for a in quran]
        vocab_src = self.rng.sample(quran, 1500)
        self.vocab = sorted({w for a in vocab_src for w in real_words(a["text"])
                             if len(normalize_arabic(w)) >= 3})
        self.nawawi = [h for h in hadith if h["source"] == NAWAWI]
        self.others = [h for h in hadith if h["source"] != NAWAWI]

    #  bookkeeping
    def add(self, text, status, source, ctype, origin=None, edit=None) -> bool:
        key = normalize_arabic(text)
        if key in self.used:
            self.rejected["duplicate"] += 1
            return False
        self.used.add(key)
        case = {"id": len(self.cases), "text": text, "expected_status": status,
                "expected_source": source, "type": ctype}
        if origin:
            case["origin"] = origin
        if edit:
            case["edit"] = edit
        self.cases.append(case)
        return True

    def fill(self, n, producer):
        """Call producer() until n cases were accepted."""
        done, tries = 0, 0
        while done < n:
            tries += 1
            if tries > n * 400:
                raise RuntimeError("Could not generate enough valid cases; relax the filters.")
            done += 1 if producer() else 0

    #  quran
    def quran_correct(self):
        n = COUNTS["correct_quran_full"]
        self.fill(n, lambda: self._q_full())
        self.fill(COUNTS["correct_quran_partial"], lambda: self._q_partial())
        self.fill(COUNTS["correct_quran_plain"], lambda: self._q_plain())

    def _q_full(self):
        a, w = self.rng.choice(self.q_words)
        if not 4 <= len(w) <= 30:
            return False
        return self.add(a["text"], "matched", "quran", "correct_quran_full", quran_origin(a))

    def _q_partial(self):
        a, w = self.rng.choice(self.q_words)
        if len(w) < 8:
            return False
        win = pick_window(w, self.rng, 5, 7)
        return self.add(" ".join(win), "matched", "quran", "correct_quran_partial", quran_origin(a))

    def _q_plain(self):
        a, w = self.rng.choice(self.q_words)
        if not 4 <= len(w) <= 30:
            return False
        return self.add(a["norma_text"], "matched", "quran", "correct_quran_plain", quran_origin(a))

    def quran_modified(self):
        kinds = ["delete", "replace", "insert"]
        per_kind = COUNTS["modified_quran"] // 3
        for kind in kinds:
            self.fill(per_kind, lambda k=kind: self._q_modified(k))

    def _q_modified(self, kind):
        a, w = self.rng.choice(self.q_words)
        if not 8 <= len(w) <= 25:
            return False
        new, edit = apply_edit(w, kind, self.rng, self.vocab)
        return self._add_modified(" ".join(w), " ".join(new), "quran", "modified_quran",
                                  quran_origin(a), edit)

    def quran_extended(self):
        self.fill(COUNTS["extended_quran"], self._q_extended)

    def _q_extended(self):
        """A real ayah start (9-10 words) followed by 2-3 invented words."""
        a, w = self.rng.choice(self.q_words)
        if len(w) < 11:
            return False
        core = w[:self.rng.randint(9, 10)]
        tail = [self.rng.choice(self.vocab) for _ in range(self.rng.randint(2, 3))]
        text = " ".join(core + tail)
        if self.corpus.contains(text):
            self.rejected["extended_in_corpus"] += 1
            return False
        return self.add(text, "matched_with_diff", "quran", "extended_quran",
                        quran_origin(a), {"kind": "append", "words": [normalize_arabic(t) for t in tail]})

    #  hadith 
    def hadith_correct(self):
        self.fill(4, lambda: self._h_correct(self.nawawi))
        self.fill(COUNTS["correct_hadith"] - 4, lambda: self._h_correct(self.others))
        self.fill(COUNTS["correct_hadith_plain"], lambda: self._h_correct(self.others, plain=True))
        self.fill(COUNTS["long_hadith"], self._h_long)

    def _h_correct(self, pool, plain=False):
        h = self.rng.choice(pool)
        seg = hadith_segment(h)
        if len(seg) < 10:
            return False
        window = pick_window(seg, self.rng, 8, 25)
        if has_chain(window):
            self.rejected["window_has_chain"] += 1
            return False
        text = " ".join(window)
        if plain:
            text = normalize_arabic(text)
        ctype = "correct_hadith_plain" if plain else "correct_hadith"
        return self.add(text, "matched", "hadith", ctype, hadith_origin(h))

    def _h_long(self):
        h = self.rng.choice(self.others)
        w = real_words(h["text"])
        if len(w) < 75:
            return False
        length = self.rng.randint(40, 60)
        start = self.rng.randint(len(w) // 3, len(w) - length)
        window = w[start:start + length]
        if has_chain(window):
            self.rejected["window_has_chain"] += 1
            return False
        return self.add(" ".join(window), "matched", "hadith",
                        "long_hadith", hadith_origin(h))

    def hadith_modified(self):
        for kind in ("delete", "replace", "insert"):
            self.fill(COUNTS["modified_hadith"] // 3, lambda k=kind: self._h_modified(k))

    def _h_modified(self, kind):
        h = self.rng.choice(self.nawawi if len(self.cases) % 4 == 0 else self.others)
        seg = hadith_segment(h)
        if len(seg) < 10:
            return False
        win = pick_window(seg, self.rng, 10, 25)
        if has_chain(win):
            self.rejected["window_has_chain"] += 1
            return False
        new, edit = apply_edit(win, kind, self.rng, self.vocab)
        return self._add_modified(" ".join(win), " ".join(new), "hadith", "modified_hadith",
                                  hadith_origin(h), edit)

    def _add_modified(self, original, modified, source, ctype, origin, edit) -> bool:
        if normalize_arabic(modified) == normalize_arabic(original):
            self.rejected["edit_changed_nothing"] += 1
            return False
        if self.corpus.contains(modified):
            self.rejected["modified_exists_in_corpus"] += 1
            return False
        return self.add(modified, "matched_with_diff", source, ctype, origin, edit)


    def famous(self):
        print("\nFamous sayings (labeled by exact-substring check):")
        for text in FAMOUS_SAYINGS:
            if len(real_words(text)) < MIN_WORDS:
                self.add(text, "too_short", "none", "famous_too_short")
                label = "too short (< 3 words) -> too_short"
            elif self.corpus.in_hadith(text):
                self.add(text, "matched", "hadith", "famous_hadith")
                label = "IN the indexed books  -> matched"
            elif self.corpus.in_quran(text):
                self.add(text, "matched", "quran", "famous_quran")
                label = "IN the Quran          -> matched"
            else:
                self.add(text, "no_reference", "none", "famous_not_in_db")
                label = "NOT in the books      -> no_reference"
            print(f"  {label} | {text}")

    def outside_scope(self):
        print("\nHadith outside the approved books / popular unsourced sayings:")
        entries = [(t, "hadith_outside_scope", note) for t, note in OUTSIDE_SCOPE_HADITH]
        entries += [(t, "popular_unsourced", "no basis as hadith") for t in POPULAR_UNSOURCED]
        for text, ctype, note in entries:
            if self.corpus.contains(text):
                print(f"  WARNING: found in the approved books -> skipped | {text}")
                self.rejected["outside_scope_in_corpus"] += 1
                continue
            self.add(text, "no_reference", "none", ctype, edit={"note": note})
            print(f"  {ctype:20} -> no_reference | {text}")

    def fabricated(self):
        for ctype, texts in (("pseudo_quran", PSEUDO_QURANIC),
                             ("general_fabricated", GENERAL_FABRICATED)):
            for text in texts:
                if self.corpus.contains(text):
                    print(f"  WARNING: '{text[:40]}...' exists in the corpus -> skipped")
                    self.rejected["fabricated_in_corpus"] += 1
                    continue
                self.add(text, "no_reference", "none", ctype)
        for text in TOO_SHORT:
            self.add(text, "too_short", "none", "short_input")

    def run(self):
        self.quran_correct()
        self.quran_modified()
        self.quran_extended()
        self.hadith_correct()
        self.hadith_modified()
        self.famous()
        self.outside_scope()
        self.fabricated()
        self.assign_split()
        return self.cases

    def assign_split(self):


        by_type = {}
        for c in self.cases:
            by_type.setdefault(c["type"], []).append(c)
        for ctype in sorted(by_type):
            group = by_type[ctype]
            self.rng.shuffle(group)
            half = (len(group) + 1) // 2
            for i, c in enumerate(group):
                c["split"] = "tune" if i < half else "test"


def main():
    parser = argparse.ArgumentParser(description="Generate Sanad's benchmark test set.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    for f in (QURAN_FILE, HADITH_FILE):
        if not f.exists():
            raise SystemExit(f"Missing {f}. Run build_normalized.py and build_hadith.py first.")

    quran = json.load(open(QURAN_FILE, encoding="utf-8"))
    hadith = json.load(open(HADITH_FILE, encoding="utf-8"))

    gen = Generator(quran, hadith, args.seed)
    cases = gen.run()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)

    print(f"\nGenerated {len(cases)} cases (seed={args.seed}) -> {args.out}")
    for ctype, n in Counter(c["type"] for c in cases).items():
        print(f"  {ctype:22} {n}")
    if gen.rejected:
        print("Rejected while generating (validation worked):", dict(gen.rejected))


if __name__ == "__main__":
    main()