import streamlit as st
import re

st.title("Тірі грамматика")

# =========================================================
# 1) Сөздік: "сөз -> сөз табы"
# POS: PRON, NOUN, VERB, ADJ, ADV, NUM, PART, CONJ, POSTP, PROPN
# =========================================================
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

    # Зат есімдер
    "сабақ": "NOUN", 
    "мектеп": "NOUN",
    "қала": "NOUN",
    "отбасы": "NOUN",
    "пойыз": "NOUN",
    "кітап": "NOUN",
    "жұмыс": "NOUN",
     "бағдарлама": "NOUN",
"ораза": "NOUN",
"алғашқы": "ADJ",
"күн": "NOUN", 

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

    "accusative": ["ны", "ні", "ды", "ді", "ты", "ті"],

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

    "participle": ["ған", "ген", "қан", "кен"]
}    # Қажетті түбірлер (скриндегі сөйлемге)
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
]

# =========================================================
# Көмекші функциялар
# =========================================================
def normalize_word(w: str) -> str:
    """Тыныс белгілерін алып, төменгі регистрге түсіру"""
    w = w.strip()
    w = re.sub(r"[^\wәіңғүұқөһӘІҢҒҮҰҚӨҺ-]", "", w)  # қазақ әріптерін сақтаймыз
    return w.lower()

def split_root_suffixes(word: str, suffixes: list[str]) -> tuple[str, list[str]]:
    """
    Сөзден соңынан қосымшаларды біртіндеп жұлып алады.
    Мыс: "сабағыммен" -> ("сабақ", ["ым","мен"])
    """
    w = normalize_word(word)
    found = []
    changed = True

    while changed:
        changed = False
        for suf in suffixes:
            if w.endswith(suf) and len(w) > len(suf) + 1:
                w = w[: -len(suf)]
                found.insert(0, suf)  # реті сақталсын
                changed = True
                break
    return w, found

def guess_pos(root: str, suffixes_found: list[str]) -> str:
    """Сөз табын жуықтау"""
    if root in DICTIONARY:
        return DICTIONARY[root]

    # Егер жіктік жалғауға ұқсас болса → етістік болуы мүмкін
    verb_like = {"мын", "мін", "быз", "біз", "сың", "сің", "сыз", "сіз"}
    if any(s in verb_like for s in suffixes_found):
        return "VERB"

    # Көптік/септік көп болса → зат есім болуы мүмкін
    noun_like = {"лар", "лер", "дар", "дер", "тар", "тер", "ға", "ге", "қа", "ке", "да", "де", "та", "те", "дан", "ден", "тан", "тен", "мен", "пен", "бен"}
    if any(s in noun_like for s in suffixes_found):
        return "NOUN"

    return "UNKNOWN"

def find_last_verb_index(items: list[dict]) -> int:
    """Сөйлемдегі соңғы етістік индексін табу"""
    idx = -1
    for i, it in enumerate(items):
        if it["pos"] == "VERB":
            idx = i
    return idx

def guess_role(pos: str, suffixes_found: list[str], index: int, last_verb_index: int) -> str:

    # Баяндауыш — соңғы етістік
    if pos == "VERB" and index == last_verb_index:
        return "Баяндауыш"

    # Бастауыш — сөйлем басындағы есімдік немесе зат есім
    if index == 0 and pos in ("PRON", "NOUN"):
        return "Бастауыш"

    # Толықтауыш — табыс/барыс септік
    object_suffixes = {"ды","ді","ты","ті","ны","ні","ға","ге","қа","ке"}
    if any(s in object_suffixes for s in suffixes_found):
        return "Толықтауыш"

    # Пысықтауыш — үстеу
    if pos == "ADV":
        return "Пысықтауыш"

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
        root, sufs = split_root_suffixes(w, SUFFIXES)
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
        role = guess_role(it["pos"], it["suffixes"], i, last_verb_index)
        suf_text = "+".join(it["suffixes"]) if it["suffixes"] else "-"
        pos_text = it["pos"]
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







