import streamlit as st
import re

st.title("Тірі грамматика")

# =========================================================
# 1) Сөздік: "сөз -> сөз табы"
# POS: PRON, NOUN, VERB, ADJ, ADV, NUM, PART, CONJ, POSTP, PROPN
# =========================================================
POS_KZ = {
    "PRON": "Есімдік",
    "NOUN": "Зат есім",
    "VERB": "Етістік",
    "ADJ": "Сын есім",
    "ADV": "Үстеу",
    "NUM": "Сан есім",
    "PART": "Шылау",
    "CONJ": "Жалғаулық",
    "POSTP": "Септеулік",
    "PROPN": "Жалқы есім"
}
DICTIONARY = {
    # Есімдіктер
    "мен": "PRON",
    "сен": "PRON",
    "сіз": "PRON",
    "ол": "PRON",
    "біз": "PRON",
    "сендер": "PRON",
    "сіздер": "PRON",
    "олар": "PRON",
    "көп": "ADV",
    "жаса": "VERB",
    "жұмыс": "NOUN",
    "жаса": "VERB",
    "айжан": "PROPN",
    "жақсы": "ADJ",
    "отыр": "VERB","бүгін":"ADV",

    # Үстеулер
    "кеше": "ADV",
    "ертең": "ADV",
    "қазір": "ADV",
    "бүгін": "ADV",

    # Зат есімдер
    "сабақ": "NOUN", 
    "мектеп": "NOUN",
    "қала": "NOUN",
    "отбасы": "NOUN",
    "пойыз": "NOUN",
    "кітап": "NOUN",
    "жұмыс": "NOUN",
     "бағдарлама": "NOUN",
    "саябақ": "NOUN",
"ораза": "NOUN",
"алғашқы": "ADJ",
"күн": "NOUN", 
"колледж": "NOUN",
"алғашқ": "ADJ",
"ай": "NOUN",
"күн": "NOUN",
"дос": "NOUN",
"серуен": "NOUN",
"айы": "NOUN",
"дос": "NOUN",
"серуенде": "VERB",

    # Жалқы есімдер (мысал)
    "алматы": "PROPN",
    "астана": "PROPN",

    # Етістік түбірлері
    "бар": "VERB",
    "кел": "VERB",
    "жүр": "VERB",
    "айт": "VERB",
    "жаз": "VERB",
    "оқы": "VERB",
    "қатыс": "VERB",
    "қатысу": "VERB",
    # Сын есім түбірлері
    "қызық": "ADJ",
 } 
POS_KZ = {
    "NOUN": "Зат есім",
    "ADJ": "Сын есім",
    "VERB": "Етістік",
    "ADV": "Үстеу",
    "PRON": "Есімдік",
    "NUM": "Сан есім",
    "CONJ": "Шылау (жалғаулық)",
    "POSTP": "Шылау (септеулік)",
    "PART": "Демеулік",
    "ADP": "Шылау",
    "PROPN": "Жалқы есім",
    "INTJ": "Одағай",
    "UNKNOWN": "Белгісіз",
}
 # ==============================
# КӘСІБИ MORPHO SUFFIX ARCHITECTURE
# ==============================

SUFFIX_GROUPS = {
    "plural": ["лар", "лер", "дар", "дер", "тар", "тер"],
    "possessive": [
        "ымыз", "іміз", "мыз", "міз",
        "ың", "ің", "ң",
        "ы", "і", "сы", "сі"
    ],

    "genitive": ["ның", "нің", "дың", "дің", "тың", "тің"],

    "dative": ["ға", "ге", "қа", "ке"],

    "accusative": [],

    "locative": ["да", "де", "та", "те"],

    "ablative": ["дан", "ден", "тан", "тен"],

    "instrumental": ["мен", "пен", "бен"],

    "verb_personal": [
        "мын", "мін", "бын", "бін", "пын", "пін",
        "мыз", "міз",
        "сың", "сің",
        "сыз", "сіз"
    ],

    "converb": ["ып", "іп", "п"],

    "participle": ["ған", "ген", "қан", "кен"],
    "past": ["ды","ді","ты","ті"]
}
}    # Қажетті түбірлер (скриндегі сөйлемге)
# Барлық suffix-терді бір тізімге жинау
SUFFIXES = []
for group in SUFFIX_GROUPS.values():
    SUFFIXES.extend(group)
DICTIONARY.update({
    "біз": "PRON",      # есімдік
    "дос": "NOUN",      # зат есім
    "және": "CONJ",     # жалғаулық
    "ұстаз": "NOUN",    # зат есім
    "бірге": "ADV",     # үстеу
    "қызық": "ADJ",     # сын есім
    "өт": "VERB",       # етістік (өтіп)
    "жатыр": "VERB",    # етістік (жатырмыз)
})

# =========================================================
# 2) Қосымшалар тізімі (жиі кездесетін)
# ҰЗЫНДАРЫН алға қойдық — дұрыс бөлу үшін!
# =========================================================
SUFFIXES = [
    # Көптік
    "лары", "лері", "дары", "дері", "тары", "тері",
    "лар", "лер", "дар", "дер", "тар", "тер",

    # Тәуелдік (жиі)
    "ымыз", "іміз",
    "лары", "лері",
    "ым", "ім", "м",
    "ың", "ің", "ң",
    "ы", "і", "сы", "сі",

    # Ілік септік
    "ның", "нің", "дың", "дің", "тың", "тің",

    # Барыс септік
    "ға", "ге", "қа", "ке",

    # Табыс септік
    "ны", "ні", "ды", "ді", "ты", "ті",

    # Жатыс септік
    "да", "де", "та", "те",
    "інде" "ында",
    "нде", "нда"

    # Шығыс септік
    "дан", "ден", "тан", "тен", "нан", "нен",

    # Көмектес септік
    "мен", "пен", "бен",

    # Етістік жіктік/шақ (өте жиі, жеңіл үлгі)
    "мын", "мін", "быз", "біз",
    "сың", "сің", "сыз", "сіз",
    "ды", "ді", "ты", "ті","дым", "дім", "тым", "тім",# көсемше (өтіп, барып...)
"ып", "іп", "п",

# жіктік жалғау (жатырмыз, барамыз...)
"мыз", "міз", "быз", "біз",
"дық", "дік", "тік", "тық",
]

# =========================================================
# Көмекші функциялар
# =========================================================
def normalize_word(w: str) -> str:
    """Тыныс белгілерін алып, төменгі регистрге түсіру"""
    w = w.strip()
    w = re.sub(r"[^\wәіңғүұқөһӘІҢҒҮҰҚӨҺ-]", "", w)  # қазақ әріптерін сақтаймыз
    return w.lower()
def layered_split(word: str, dictionary: dict):
    """Түбір+қосымшаны тұрақты бөлу: тек сөздік дәлел болса ғана кеседі."""
    w = normalize_word(word)
    found = []

    # Реттік сан есім жұрнағын бөлмейміз: екінші, үшінші, төртінші...
    if w.endswith(("інші", "ншы")):
        return w, []

    if w in dictionary:
        return w, found

    # Ұзын қосымшалар алдымен тексерілсін
    # Барлық қосымшаларды SUFFIX_GROUPS-тен жинаймыз
    all_suffixes = []
    for group in SUFFIX_GROUPS.values():
        all_suffixes.extend(group)
  
    suffixes = sorted(all_suffixes, key=len, reverse=True)

    changed = True
    while changed:
        changed = False

        if w in dictionary:
            break

        for suf in suffixes:
            if w.endswith(suf) and len(w) > len(suf) + 1:
                cand = w[:-len(suf)]
                if cand in dictionary:
                    w = cand
                    found.insert(0, suf)
                    changed = True
                    break

    return w, found

def guess_pos(root: str, suffixes_found: list[str]) -> str:
    """Сөз табын жуықтау"""

    if root in DICTIONARY:
        return DICTIONARY[root]

    # Реттік сан есім
    if root.endswith(("інші", "ншы")):
        return "NUM"

    # Егер жіктік жалғау болса
    verb_like = {"мын", "мін", "быз", "біз", "сың", "сің"}
    if any(s in verb_like for s in suffixes_found):
        return "VERB"

    return "UNKNOWN"

    # Көптік/септік көп болса → зат есім болуы мүмкін
    noun_like = {"лар", "лер", "дар", "дер", "тар", "тер", "ға", "ге", "қа", "ке", "да", "де", "та", "те", "дан", "ден", "тан", "тен", "мен", "пен", "бен"}
    if any(s in noun_like for s in suffixes_found):
        return "NOUN"
# Реттік сан есімдер (-ншы/-нші/-ыншы/-інші)
    ordinal_like = {"ншы", "нші", "ыншы", "інші"}
    if any(s in ordinal_like for s in suffixes_found):
        return "NUM"
# Жатыс септігі (-нда/-нде/-ында/-інде)
    locative_like = {"нда", "нде", "ында", "інде"}
    if any(s in locative_like for s in suffixes_found):
        return "NOUN"
 # Туынды зат есім (-лық/-лік/-дық/-дік/-тық/-тік)
    noun_deriv = {"лық", "лік", "дық", "дік", "тық", "тік"}
    if any(s in noun_deriv for s in suffixes_found):
        return "NOUN"       
    return "UNKNOWN"

def find_last_verb_index(items: list[dict]) -> int:
    """Сөйлемдегі соңғы етістік индексін табу"""
    idx = -1
    for i, it in enumerate(items):
        if it["pos"] == "VERB":
            idx = i
    return idx
def guess_role(pos: str, suffixes_found: list[str], index: int, last_verb_index: int, items: list[dict]) -> str:

    # Баяндауыш — соңғы етістік
    if pos == "VERB" and index == last_verb_index:
        return "Баяндауыш"
    # Бастауыш – баяндауыштан бұрын тұрған атау септіктегі зат есім/есімдік
    if pos in ("PRON", "NOUN") and index < last_verb_index:
        # Егер жалғаулары жоқ болса (атау септік)
        if not suffixes_found:
            return "Бастауыш"

    # Бастауыш — сөйлем басындағы есімдік немесе зат есім
    if index == 0 and pos in ("PRON", "NOUN"):
        return "Бастауыш"
    # Сын есім зат есімнің алдында тұрса → анықтауыш
    if pos == "ADJ" and index + 1 < len(items):
        if items[index + 1]["pos"] in ("NOUN", "PROPN"):
            return "Анықтауыш"

    # Толықтауыш — табыс/барыс септік
    object_suffixes = {"ды","ді","ты","ті","ны","ні","ға","ге","қа","ке"}
    if any(s in object_suffixes for s in suffixes_found):
        return "Толықтауыш"

    # Пысықтауыш — үстеу
    if pos == "ADV":
        return "Пысықтауыш"
    if pos in ("ADJ", "NUM") and index < last_verb_index:
        return "Анықтауыш"

    return "Белгісіз"

# =========================================================
# UI
# =========================================================
text = st.text_input("Сөйлем жазыңыз:")

if text:
    st.write("Сіз жаздыңыз:", text)

    raw_words = text.split()
    analysis = []

    # Әр сөзді талдау
    for w in raw_words:
        root, sufs = layered_split(w, DICTIONARY)
        pos = guess_pos(root, sufs)
        analysis.append({
            "orig": w,
            "root": root,
            "suffixes": sufs,
            "pos": pos,
        })

    last_verb_index = find_last_verb_index(analysis)

    # Кесте үшін мәлімет
    table = []
    for i, it in enumerate(analysis):
        def guess_role(pos: str, suffixes_found: list[str], index: int, last_verb_index: int, items: list[dict]) -> str:
        suf_text = "+".join(it["suffixes"]) if it["suffixes"] else "-"
        pos_text = POS_KZ.get(it["pos"], it["pos"])
        table.append({
            "Сөз": it["orig"],
            "Түбір": it["root"] if it["root"] else "-",
            "Қосымша(лар)": suf_text,
            "Сөз табы": pos_text,
            "Сөйлем мүшесі": role
        })

    st.subheader("Талдау нәтижесі")
    st.table(table)

    # Қате болуы мүмкін сөздер (түбір сөздікте жоқ болса)
    st.subheader("Сөздікте жоқ түбірлер (қате болуы мүмкін)")
    unknowns = [it for it in analysis if (it["root"] not in DICTIONARY)]
    if not unknowns:
        st.success("Барлық түбірлер сөздікте бар сияқты ✅")
    else:
        for it in unknowns:
            st.warning(f"'{it['orig']}' → түбірі '{it['root']}' (сөздікте жоқ)")

        st.info("Кеңес: төмендегі DICTIONARY ішіне осы түбірлерді қосып көріңіз.")
















































