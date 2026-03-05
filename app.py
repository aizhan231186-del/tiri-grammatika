import streamlit as st
import re

def extract_features(pos, sufs):
    feats = {}

    if pos == "PRED":
        feats["Pred"] = "Yes"

    if pos == "NOUN":
        if any(s in ["лар","лер","дар","дер","тар","тер"] for s in sufs):
            feats["Number"] = "Plur"

        if any(s in ["ның","нің","дың","дің","тың","тің"] for s in sufs):
            feats["Case"] = "Gen"

        elif any(s in ["ға","ге","қа","ке"] for s in sufs):
            feats["Case"] = "Dat"

        elif any(s in ["ны","ні","ды","ді","ты","ті"] for s in sufs):
            feats["Case"] = "Acc"

        elif any(s in ["да","де","та","те"] for s in sufs):
            feats["Case"] = "Loc"

        elif any(s in ["дан","ден","тан","тен"] for s in sufs):
            feats["Case"] = "Abl"

    if pos == "VERB":
        if any(s in ["ды","ді","ты","ті"] for s in sufs):
            feats["Tense"] = "Past"

    return feats

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
    "айжан": "PROPN",
    "жақсы": "ADJ",
    "отыр": "VERB",
    "бүгін":"ADV",
    "қазақ": "NOUN",
"тіл": "NOUN",
"сабақ": "NOUN",
"ұна": "VERB",
    "адам": "NOUN",
    "отбасы": "NOUN",
    "бар": "VERB",   # немесе "AUX"/"VERB" деп өзің қалай ұстасаң

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
    "студент": "NOUN",
    "әдебиет": "NOUN",
    "кітап": "NOUN",
    "тапсырма": "NOUN",
    "дүкен": "NOUN",

    # Жалқы есімдер (мысал)
    "алматы": "PROPN",
    "астана": "PROPN",
    "Тараз": "PRON",
    "Қазақстан": "PRON",

    # Етістік түбірлері
    "кел": "VERB",
    "жүр": "VERB",
    "айт": "VERB",
    "жаз": "VERB",
    "оқы": "VERB",
    "қатыс": "VERB",
    "қатысу": "VERB",
    "бол": "VERB",
    "ойна": "VERB",
    "орында": "VERB",
    "бар": "VERB",
    "жоқ": "PRED",
    
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
    "PRED": "Предекатив сөз",
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
    "ablative": ["дан","ден","тан","тен","нан","нен"],
    "instrumental": ["мен","пен","бен"],

    # етістікке
    "past": [ 
          "ды", "ді", "ты", "ті"   
    ], 
    "present_3sg": ["йды", "йді", "ады", "еді"],
    "present_y": ["й"],                                       # бар-ды-қ
    "verb_personal_1pl": ["мыз","міз"],     # бар-ды-қ (мұнда -қ өзі көптік жақ)
    "converb": ["ып","іп","п"],
    "participle": ["ған","ген","қан","кен"],
    "infinitive_u": ["у"],
}
CASE_MAP = {
    # Ілік септік
    "ның": "Ілік септік", "нің": "Ілік септік",
    "дың": "Ілік септік", "дің": "Ілік септік",
    "тың": "Ілік септік", "тің": "Ілік септік",

    # Барыс септік
    "ға": "Барыс септік", "ге": "Барыс септік",
    "қа": "Барыс септік", "ке": "Барыс септік",

    # Табыс септік
    "ны": "Табыс септік", "ні": "Табыс септік",
    "ды": "Табыс септік", "ді": "Табыс септік",
    "ты": "Табыс септік", "ті": "Табыс септік",

    # Жатыс септік
    "да": "Жатыс септік", "де": "Жатыс септік",
    "та": "Жатыс септік", "те": "Жатыс септік",

    # Шығыс септік
    "дан": "Шығыс септік", "ден": "Шығыс септік",
    "тан": "Шығыс септік", "тен": "Шығыс септік",
    "нан": "Шығыс септік", "нен": "Шығыс септік",

    # Көмектес септік
    "мен": "Көмектес септік", "пен": "Көмектес септік", "бен": "Көмектес септік",
}
TENSE_MAP = {
    "past": "Өткен шақ",
    "converb": "Көсемше",
    "participle": "Есімше",
}
# Барыс септік формалары
DATIVE_FORMS = {"ға", "ге", "қа", "ке"}
def format_suffixes(suffixes):
    result = []
    for suf in suffixes:
        if suf in CASE_MAP:
            result.append(CASE_MAP[suf])
        elif suf in TENSE_MAP:
            result.append(TENSE_MAP[suf])
        else:
            result.append(suf)
    return " + ".join(result)

def detect_category(pos, suffixes):
    categories = []

    # 1) Егер ЕТІСТІК болса: "ды/ді/ты/ті" — септік емес, етістік форманты!
    if pos == "VERB":
        # ауыспалы осы шақ (3-жақ): ұна-й-ды / бар-а-ды / кел-е-ді
        has_link = any(x in suffixes for x in ["й", "а", "е"])
        has_di   = any(x in suffixes for x in ["ды", "ді"])
        has_ti   = any(x in suffixes for x in ["ты", "ті"])

        if has_link and has_di:
            categories.append("Ауыспалы осы шақ (3-жақ)")
        elif has_di or has_ti:
            categories.append("Өткен шақ")

        # көсемше/есімше (қаласаң қалдырасың)
        if any(x in suffixes for x in ["ып", "іп", "п"]):
            categories.append("Көсемше")
        if any(x in suffixes for x in ["ған", "ген", "қан", "кен"]):
            categories.append("Есімше")
        # ✅ Тұйық етістік (-у)
        if "у" in suffixes:
            categories.append("Тұйық етістік")   
        # ✅ Тұйық етістікке септік жалғанса: орындау+да, бару+ға, келу+ден
        for s in suffixes:
            if s in CASE_MAP:
                categories.append(CASE_MAP[s])

        return " + ".join(dict.fromkeys(categories)) if categories else "—"

    # 2) ЕТІСТІК ЕМЕС болса (зат есім/есімдік): септіктерді осында қара
    for suf in suffixes:
        if suf in CASE_MAP:
            categories.append(CASE_MAP[suf])
        elif suf in ["ы", "і", "сы", "сі", "м", "ң", "ңыз", "ңіз", "ымыз", "іміз"]:
            categories.append("Тәуелдік жалғау")
        elif suf in ["лар", "лер", "дар", "дер", "тар", "тер"]:
            categories.append("Көптік жалғау")

    return " + ".join(dict.fromkeys(categories)) if categories else "—"
# Қажетті түбірлер (скриндегі сөйлемге)
# Барлық suffix-терді бір тізімге жинау
SUFFIXES = []
for group in SUFFIX_GROUPS.values():
    SUFFIXES.extend(group)
SUFFIXES = sorted(SUFFIXES, key=len, reverse=True)   
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
# =========================================================
# Көмекші функциялар
# =================================================
def normalize_word(w: str) -> str:
    """Тыныс белгілерін алып, төменгі регистрге түсіру"""
    w = w.strip()
    w = re.sub(r"[^\wәіңғүұқөһӘІҢҒҮҰҚӨҺ-]", "", w)  # қазақ әріптерін сақтаймыз
    return w.lower()
def layered_split(word: str, dictionary: dict):
    """Түбір + қосымшаны қабаттап бөлу (аралық формалар сөздікте болмаса да кеседі)."""
    w = normalize_word(word)
    SPECIAL_FORMS = {
    "маған": ("мен", ["ға"]),
    "саған": ("сен", ["ға"]),
    "оған": ("ол", ["ға"]),
    "менің": ("мен", ["нің"]),
    "сенің": ("сен", ["нің"]),
    "оның": ("ол", ["ның"]),
    "біздің": ("біз", ["дің"]),
    "сіздің": ("сіз", ["дің"]),
    "олардың": ("олар", ["дың"]),
}
    # түбірді табатын функцияның басына:
    w = word.lower()
    if w in SPECIAL_FORMS:
        return SPECIAL_FORMS[w][0], SPECIAL_FORMS[w][1] 
    
    # 🔥 Сан есімдерді бөлмейміз
    NUMERALS = {
        "бір","екі","үш","төрт","бес","алты","жеті","сегіз","тоғыз","он",
        "жиырма","отыз","қырық","елу","алпыс","жетпіс",
        "сексен","тоқсан","жүз","мың"
    }
    # 🔥 Егер сөз толық сан есім болса — бөлме
    if w in NUMERALS:
        return w, []
    found = []

    # Реттік сан есім жұрнағын бөлмейміз (екінші, үшінші...)
    if w.endswith(("інші", "ншы")):
        return w, []

    # Барлық қосымшаларды SUFFIX_GROUPS-тен жинаймыз
    all_suffixes = []
    for group_name, group in SUFFIX_GROUPS.items():
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
                cand = w[:-len(suf)]

                # ✅ "отбасым" сияқты: түбір "отбасы", тәуелдік "м"
                if suf == "ым" and (cand + "ы") in dictionary:
                    w = cand + "ы"
                    found.insert(0, "м")
                    changed = True
                    break

                if suf == "ім" and (cand + "і") in dictionary:
                    w = cand + "і"
                    found.insert(0, "м")
                    changed = True
                    break

                # 🔥 қ/к -> ғ/г болып өзгергенін кері қайтару (көбіне тәуелдік: ы/і)
                if suf in ("ы", "і"):
                    if cand.endswith("ғ"):
                        cand = cand[:-1] + "қ"
                    elif cand.endswith("г"):
                        cand = cand[:-1] + "к"
                # ✅ "әдебиеті" сияқты: root соңында "т" жоғалып кетпесін
                # егер suf == "ті" болса, бұл көбіне "т" түбірдің бөлігі + "і" тәуелдік
                if suf == "ті" and (cand + "т") in dictionary:
                    w = cand + "т"
                    found.insert(0, "і")
                    changed = True
                    break

                elif suf == "ты" and (cand + "т") in dictionary:
                    w = cand + "т"
                    found.insert(0, "ы")
                    changed = True
                    break

                # ✅ Б/П дыбыс алмасуын кері қайтару (кітаб -> кітап)
                if cand.endswith("б") and (cand[:-1] + "п") in dictionary:
                    cand = cand[:-1] + "п"

                # ✅ Ғ/Қ дыбыс алмасуы
                if cand.endswith("ғ") and (cand[:-1] + "қ") in dictionary:
                    cand = cand[:-1] + "қ"
                w = cand
                # "йды/йді" және "ады/еді" сияқты құрама қосымшаларды бөлу
                if suf in ("йды", "йді"):
                    found.insert(0, "ды" if suf == "йды" else "ді")
                    found.insert(0, "й")
                elif suf in ("ады", "еді"):
                    found.insert(0, "ды" if suf == "ады" else "ді")
                    found.insert(0, "а" if suf == "ады" else "е")
                else:
                    found.insert(0, suf)
                changed = True
                break

    # 🔥 Нормализация — while БІТКЕННЕН КЕЙІН
    if w.endswith("й"):
        w = w[:-1]

    return w, found

def guess_pos(root: str, suffixes_found: list[str]) -> str:
    # 🔥 Сан есімдер тізімі
    NUMERALS = {"бір","екі","үш","төрт","бес","алты","жеті","сегіз","тоғыз","он",
    "жиырма","отыз","қырық","елу","алпыс","жетпіс","сексен","тоқсан","жүз","мың"}

    # 🔥 Егер түбір сан есім болса
    if root in NUMERALS:
        return "NUM"
    # Сөз табын жуықтау

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
    if any(s in ["лар","лер","дар","дер","тар","тер"] for s in suffixes_found):
        return "NOUN"

    # Жатыс септік -> көбіне зат есім (далада, мектепте)
    if any(s in ["да","де","та","те"] for s in suffixes_found):
        return "NOUN"

    # Көсемше -> етістік (ойнап/оқып/келіп)
    if any(s in ["п","ып","іп"] for s in suffixes_found):
        return "VERB"
        
    return "UNKNOWN"
    
    from typing import List, Dict
    def extract_features(pos: str, root: str, suffixes: List[str]) -> Dict:
        feats = {}
        
        # 🔥 Предикативтер (бар/жоқ)
        if pos =="PRED":
            if root == "бар":
                feats["PredType"] = "Exist"
            elif root == "жоқ":
                feats["PredType"] = "Absent"
        # ... ары қарай басқа NOUN/VERB шарттарың осында жалғасады ...
        return feats

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
        if it["pos"] in ("VERB","PRED"):
            idx = i
    return idx
def guess_role(pos: str, suffixes_found: list[str], index: int, last_verb_index: int, items: list[dict]) -> str:
    # 0-индекстегі және соңында үтірі бар сөз -> қаратпа сөз
    if index == 0 and items[index].get("has_comma"):
        return "Қаратпа сөз"
    
    # ✅ Предикатив сөз → баяндауыш
    if pos == "PRED":
        return "Баяндауыш"
    # Баяндауыш — соңғы етістік
    if pos == "VERB" and index == last_verb_index:
        return "Баяндауыш"
    # Егер екі етістік қатар келсе (ойнап жүр, барып келді) -> күрделі баяндауыш
    if pos == "VERB" and index < last_verb_index and index + 1 < len(items):
        if items[index + 1]["pos"] == "VERB":
           return "Баяндауыш"

    # ✅ Ілік септіктегі есімдік/зат есім келесі NOUN/PROPN алдында тұрса → Анықтауыш
    if any(s in ["ның","нің","дың","дің","тың","тің"] for s in suffixes_found):
        if index + 1 < len(items) and items[index + 1]["pos"] in ("NOUN","PROPN"):
            return "Анықтауыш"
    # 🔥 Сан есім + зат есім → анықтауыш
    if pos == "NUM":
        if index + 1 < len(items) and items[index + 1]["pos"] in ("NOUN","PROPN"):
            return "Анықтауыш"

    # 🔥 Егер жатыс септік болса → Пысықтауыш
    if any(s in ["да", "де", "та", "те"] for s in suffixes_found):
        return "Пысықтауыш" 

    # 🔥 Егер атау септіктегі зат есім және баяндауыштан бұрын тұрса → Бастауыш
    if (
        pos == "NOUN"
        and index < last_verb_index
        and not any(s in CASE_MAP for s in suffixes_found)
    ):
        return "Бастауыш"
    # Егер зат есімнің алдында тағы зат есім тұрса → анықтауыш
    if pos == "NOUN" and index + 1 < len(items):
        if items[index + 1]["pos"] == "NOUN":
            return "Анықтауыш"
    # Егер соңғы етістіктің алдында тұрған зат есім болса → бастауыш
    # if (
    #     pos == "NOUN"
    #     and index == last_verb_index - 1
    #     and not any(s in DATIVE_FORMS for s in suffixes_found)
    # ):
    #     return "Бастауыш" 

    # Егер DAT болса — толықтауыш (маған/саған/оған)
    
    # Бастауыш — сөйлем басындағы есімдік/зат есім (DAT болмасын)
    # if index == 0 and pos in ("PRON", "NOUN", "PROPN") and "DAT" not in suffixes_found:
    #     return "Бастауыш"  

    # Сын есім зат есімнің алдында тұрса -> анықтауыш (қорғаныс: index+1 шектен аспасын)
    if pos == "ADJ" and index + 1 < len(items):
        if items[index + 1]["pos"] in ("NOUN", "PROPN"):
            return "Анықтауыш"
    # Жатыс септік (да/де/та/те) -> пысықтауыш
    if any(s in {"да","де","та","те"} for s in suffixes_found):
        return "Пысықтауыш"

    # Толықтауыш — табыс/барыс септік
    object_suffixes = {"ны", "ні", "ға", "ге", "қа", "ке",}
    if any(s in DATIVE_FORMS for s in suffixes_found):
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
    for idx, w in enumerate(raw_words):
        has_comma = w.endswith(",")
        clean_w = normalize_word(w)
        root, sufs = layered_split(clean_w, DICTIONARY)
        pos = guess_pos(root, sufs)
        
    # БАР сөзін контекстпен түзету
    if root == "бар":
        if analysis and analysis[-1]["feats"] == "Барыс септік":
            pos = "VERB"
        else:
            pos = "PRED"

    # ТҰР/ЖАТЫР/ОТЫР/ЖҮР
    if root in ["тұр","жатыр","отыр","жүр"]:
        if analysis and "Көсемше" in analysis[-1]["feats"]:
            pos = "AUX"
        else:
            pos = "VERB"
    feats = extract_features(pos, sufs)

    analysis.append({
            "orig": w,
            "root": root,
            "suffixes": sufs,
            "pos": pos,
            "feats": feats, 
            "has_comma": has_comma,
    })
    last_verb_index = find_last_verb_index(analysis)

    table = []
    for i, it in enumerate(analysis):
        role = guess_role(it["pos"], it["suffixes"], i, last_verb_index, analysis)

        suf_text = "+".join(it["suffixes"]) if it["suffixes"] else "—"
        category_text = detect_category(it["pos"], it["suffixes"]) # ✅ МІНЕ ОСЫ
        pos_text = POS_KZ.get(it["pos"], it["pos"])

        table.append({
            "Сөз": it["orig"],
            "Түбір": it["root"] if it["root"] else "—",
            "Қосымша(лар)": suf_text,
            "Грамматикалық категория": category_text,      # ✅ ЖАҢА БАҒАН
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













































































































































