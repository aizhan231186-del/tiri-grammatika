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
"түн": "NOUN",
"колледж": "NOUN",
"алғашқ": "ADJ",
"ай": "NOUN",
"күн": "NOUN",
"дос": "NOUN",
"серуен": "NOUN",
"айы": "NOUN",
    "бала": "NOUN",
    "дала": "NOUN",
"серуенде": "VERB",
    "жел": "NOUN",

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
    "бол": "VERB",
    "ойна": "VERB",
    
    # Сын есім түбірлері
    "қызық": "ADJ",
    "қатты": "ADJ",
    "жұмсақ": "ADJ",
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
    "poss_1sg": ["ым","ім"],
    "poss_2sg": ["ың","ің"],
    "poss_3sg": ["ы","і","сы","сі"],
    "poss_1pl": ["ымыз","іміз"],
    "poss_2pl": ["сыңдар","сіңдер","сыңыз","сіңіз"],  # ықшамдап алуға болады
    "genitive": ["ның","нің","дың","дің","тың","тің"],
    "dative": ["ға","ге","қа","ке"],
    "accusative": ["ны","ні","ды","ді","ты","ті"],
    "locative": ["да","де","та","те"],
    "ablative": ["дан","ден","тан","тен"],
    "instrumental": ["мен","пен","бен"],

    # етістікке
    "past": ["ды","ді","ты","ті"],          # бар-ды-қ
    "verb_personal_1pl": ["мыз","міз"],     # бар-ды-қ (мұнда -қ өзі көптік жақ)
    "converb": ["ып","іп","п"],
    "participle": ["ған","ген","қан","кен"],
}
# Қажетті түбірлер (скриндегі сөйлемге)
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
    """Түбір + қосымшаны қабаттап бөлу (аралық формалар сөздікте болмаса да кеседі)."""
    w = normalize_word(word)
    found = []

    # Реттік сан есім жұрнағын бөлмейміз (екінші, үшінші...)
    if w.endswith(("інші", "ншы")):
        return w, []

    # Барлық қосымшаларды SUFFIX_GROUPS-тен жинаймыз
    all_suffixes = []
    for group in SUFFIX_GROUPS.values():
        all_suffixes.extend(group)

    # Ұзын қосымша алдымен тексерілсін
    suffixes = sorted(set(all_suffixes), key=len, reverse=True)

    changed = True
    while changed:
        changed = False
        if w in dictionary:
            break

        for suf in suffixes:
            if w.endswith(suf) and len(w) > len(suf) + 1:
                # кесіп көреміз
                cand = w[:-len(suf)]

                # Қосымшаны алып тастай береміз (cand сөздікте болмаса да)
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
    # Көптік жалғау -> зат есім
    if any(s in ["лар","лер","дар","дер","тар","тер"] for s in sufs):
        return "NOUN"

    # Жатыс септік -> көбіне зат есім (далада, мектепте)
    if any(s in ["да","де","та","те"] for s in sufs):
        return "NOUN"

    # Көсемше -> етістік (ойнап/оқып/келіп)
    if any(s in ["п","ып","іп"] for s in sufs):
        return "VERB"
    return "UNKNOWN"
    def extract_features(pos: str, suffixes: list[str]) -> dict:
        feats = {}

        # NOUN features
        if pos == "NOUN":
            if any(s in SUFFIX_GROUPS["plural"] for s in suffixes):
                feats["Number"] = "Plur"
        if any(s in SUFFIX_GROUPS["poss_1pl"] for s in suffixes):
            feats["Poss"] = "1Pl"
        elif any(s in SUFFIX_GROUPS["poss_1sg"] for s in suffixes):
            feats["Poss"] = "1Sg"
        elif any(s in SUFFIX_GROUPS["poss_2sg"] for s in suffixes):
            feats["Poss"] = "2Sg"
        elif any(s in SUFFIX_GROUPS["poss_3sg"] for s in suffixes):
            feats["Poss"] = "3Sg"

        if any(s in SUFFIX_GROUPS["genitive"] for s in suffixes):
            feats["Case"] = "Gen"
        elif any(s in SUFFIX_GROUPS["dative"] for s in suffixes):
            feats["Case"] = "Dat"
        elif any(s in SUFFIX_GROUPS["accusative"] for s in suffixes):
            feats["Case"] = "Acc"
        elif any(s in SUFFIX_GROUPS["locative"] for s in suffixes):
            feats["Case"] = "Loc"
        elif any(s in SUFFIX_GROUPS["ablative"] for s in suffixes):
            feats["Case"] = "Abl"
        elif any(s in SUFFIX_GROUPS["instrumental"] for s in suffixes):
            feats["Case"] = "Ins"

    # VERB features
    if pos == "VERB":
        if any(s in SUFFIX_GROUPS["past"] for s in suffixes):
            feats["Tense"] = "Past"

    return feats

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
def guess_role(pos: str, suffixes_found: list[str], index: int, last_verb_index: int, items: list):
    # Баяндауыш — соңғы етістік
    if pos == "VERB" and index == last_verb_index:
        return "Баяндауыш"
    # Егер екі етістік қатар келсе (ойнап жүр, барып келді) → күрделі баяндауыш
    if pos == "VERB" and index < last_verb_index and items[index + 1]["pos"] == "VERB":
        return "Баяндауыш"  
    # Жатыс септік (да/де/та/те) -> пысықтауыш
    if any(s in ["да","де","та","те"] for s in suffixes_found):
        return "Пысықтауыш"
    # Бастауыш — сөйлем басындағы есімдік немесе зат есім
    if index == 0 and pos in ("PRON", "NOUN", "PROPN"):
        return "Бастауыш"

    # Сын есім зат есімнің алдында тұрса → анықтауыш
    if pos == "ADJ":
        return "Анықтауыш"
    # Егер зат есім баяндауыштан бұрын тұрса -> бастауыш
    if pos in ("NOUN", "PROPN") and index < last_verb_index:
        return "Бастауыш"
    # Толықтауыш — табыс/барыс септік
    object_suffixes = {"ны", "ні", "ға", "ге", "қа", "ке"}
    if any(s in object_suffixes for s in suffixes_found):
        return "Толықтауыш"

    # Пысықтауыш — үстеу
    if pos == "ADV":
        return "Пысықтауыш"

    # Қалған ADJ/NUM көбіне анықтауыш болып келеді (етістіктен бұрын)
    if pos in ("ADJ", "NUM") and index < last_verb_index:
        return "Анықтауыш"
    # Көмектес септік (мен/пен/бен) → пысықтауыш
    if any(s in ["мен","пен","бен"] for s in suffixes_found):
        return "Пысықтауыш"
    # Барыс септік (қа/ке/ға/ге)
    if any(s in ["қа","ке","ға","ге"] for s in suffixes_found):
        # соңғы етістік (баяндауыш) түбірін аламыз
        last_word = items[last_verb_index]["root"]

        # қозғалыс етістіктері болса -> мекен/бағыт пысықтауыш болуы мүмкін
        if last_word in ["бар", "кел", "кет", "жүр", "шық"]:
            return "Пысықтауыш"
    else:
        return "Толықтауыш"
    return "Белгісіз"
def extract_features(pos, sufs):
    return {}

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
        feats = extract_features(pos, sufs)   

        analysis.append({
            "orig": w,
            "root": root,
            "suffixes": sufs,
            "pos": pos,
            "feats": feats,                  
        })
    last_verb_index = find_last_verb_index(analysis)

    # Кесте үшін мәлімет
    table = []
    
    for i, it in enumerate(analysis):
        role = guess_role(it["pos"], it["suffixes"], i, last_verb_index, items)
        suf_text = "+".join(it["suffixes"]) if it["suffixes"] else "—"
        pos_text = POS_KZ.get(it["pos"], it["pos"])

        table.append({
            "Сөз": it["orig"],
            "Түбір": it["root"] if it["root"] else "—",
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














































































