
import streamlit as st
import json
import difflib

# Lade Kursdaten
with open("kursdaten.json", "r", encoding="utf-8") as f:
    kurse = json.load(f)

# Unterstützte Sprachen
languages = {
    "Deutsch": "de",
    "Français": "fr",
    "Italiano": "it"
}

# Sprachspezifische Texte
texts = {
    "de": {
        "title": "Kurs-Chatbot",
        "intro": "Willkommen! Ich helfe dir, den passenden Kurs zu finden.",
        "ask_category": "Wähle eine Kurskategorie aus:",
        "ask_topic": "Wähle ein Software-Thema (optional):",
        "ask_keywords": "Nach welchem Thema oder Begriff suchst du?",
        "ask_duration": "Wie viele Stunden darf der Kurs höchstens dauern?",
        "no_matches": "Es wurde kein Kurs gefunden, der alle Kriterien erfüllt. Hier sind stattdessen die nächsten Treffer:",
        "results": "Hier sind die 3 passendsten Kurse:",
        "no_results": "Leider wurden keine passenden Kurse gefunden.",
    },
    "fr": {
        "title": "Chatbot de formation",
        "intro": "Bienvenue ! Je vous aide à trouver le bon cours.",
        "ask_category": "Choisissez une catégorie de cours :",
        "ask_topic": "Choisissez un thème logiciel (facultatif) :",
        "ask_keywords": "Quel thème ou mot-clé recherchez-vous ?",
        "ask_duration": "Quelle est la durée maximale du cours (en heures) ?",
        "no_matches": "Aucun cours ne correspond à tous les critères. Voici les résultats les plus proches :",
        "results": "Voici les 3 cours les plus adaptés :",
        "no_results": "Aucun cours correspondant trouvé.",
    },
    "it": {
        "title": "Chatbot dei corsi",
        "intro": "Benvenuto! Ti aiuto a trovare il corso giusto.",
        "ask_category": "Seleziona una categoria di corso:",
        "ask_topic": "Seleziona un software (facoltativo):",
        "ask_keywords": "Quale tema o parola chiave stai cercando?",
        "ask_duration": "Quante ore al massimo dovrebbe durare il corso?",
        "no_matches": "Nessun corso soddisfa tutti i criteri. Ecco i risultati più vicini:",
        "results": "Ecco i 3 corsi più adatti:",
        "no_results": "Nessun corso trovato.",
    }
}

# Streamlit-Einstellungen
st.set_page_config(page_title="Kurs-Chatbot", layout="centered")
st.sidebar.title("🌐 Sprache / Langue / Lingua")
language_choice = st.sidebar.radio("Sprache wählen:", list(languages.keys()))
lang = languages[language_choice]
t = texts[lang]

# UI Inhalte
st.title(t["title"])
st.write(t["intro"])

# Filter: Kategorie auswählen
available_categories = sorted(set(k["category"] for k in kurse if k["category"]))
selected_category = st.radio(t["ask_category"], available_categories)

# Filter: Thema/Software extrahieren aus Titeln (z. B. Word, Excel)
software_keywords = ["Word", "Excel", "Teams", "PowerPoint", "Outlook", "Microsoft", "Windows", "OneNote"]
topics_found = sorted({w for k in kurse for w in software_keywords if w.lower() in k["title"].lower()})
selected_topic = st.selectbox(t["ask_topic"], [""] + topics_found)

# Filter: Schlagwortsuche
keywords = st.text_input(t["ask_keywords"])

# Filter: Maximaldauer
max_duration = st.slider(t["ask_duration"], 1.0, 20.0, 8.0, step=0.5)

# Kurs filtern
def relevance_score(kurs, keywords, max_duration):
    score = 0
    if kurs["category"] != selected_category:
        return 0
    if selected_topic and selected_topic.lower() not in kurs["title"].lower():
        return 0
    text = f"{kurs['title']} {kurs['description']} {kurs['category']}".lower()
    for word in keywords.lower().split():
        if word in text:
            score += 3
        elif difflib.get_close_matches(word, text.split(), n=1, cutoff=0.8):
            score += 1
    return score

if keywords or selected_topic:
    matching_kurse = [
        k for k in kurse
        if k["language"] == language_choice and k["category"] == selected_category
    ]
    ranked = sorted(matching_kurse, key=lambda k: relevance_score(k, keywords, max_duration), reverse=True)
    top_matches = [k for k in ranked if k["duration_hours"] <= max_duration and relevance_score(k, keywords, max_duration) > 0][:3]

    if not top_matches:
        fallback_matches = sorted(matching_kurse, key=lambda k: relevance_score(k, keywords, max_duration), reverse=True)[:3]
        if fallback_matches:
            st.warning(t["no_matches"])
            top_matches = fallback_matches
        else:
            st.error(t["no_results"])

    if top_matches:
        st.subheader(t["results"])
        for k in top_matches:
            with st.expander(k["title"]):
                st.markdown(f"**🗣 Sprache:** {k['language']}")
                st.markdown(f"**⏱ Dauer:** {k['duration_hours']} Std.")
                st.markdown(f"**👥 Zielgruppe:** {k['target_group']}")
                st.markdown(f"**🧭 Kategorie:** {k['category']}")
                st.markdown(f"**📝 Beschreibung:**

{k['description']}")
