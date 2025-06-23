
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
        "ask_language": "In welcher Sprache soll der Kurs sein?",
        "ask_keywords": "Nach welchem Thema oder Begriff suchst du?",
        "ask_duration": "Wie viele Stunden darf der Kurs höchstens dauern?",
        "results": "Hier sind die 3 passendsten Kurse:",
        "no_results": "Leider wurden keine passenden Kurse gefunden."
    },
    "fr": {
        "title": "Chatbot de formation",
        "intro": "Bienvenue ! Je vous aide à trouver le bon cours.",
        "ask_language": "Dans quelle langue le cours doit-il être dispensé ?",
        "ask_keywords": "Quel thème ou mot-clé recherchez-vous ?",
        "ask_duration": "Quelle est la durée maximale du cours (en heures) ?",
        "results": "Voici les 3 cours les plus adaptés :",
        "no_results": "Aucun cours correspondant trouvé."
    },
    "it": {
        "title": "Chatbot dei corsi",
        "intro": "Benvenuto! Ti aiuto a trovare il corso giusto.",
        "ask_language": "In quale lingua dovrebbe essere il corso?",
        "ask_keywords": "Quale tema o parola chiave stai cercando?",
        "ask_duration": "Quante ore al massimo dovrebbe durare il corso?",
        "results": "Ecco i 3 corsi più adatti:",
        "no_results": "Nessun corso trovato."
    }
}

# Sprache wählen
st.set_page_config(page_title="Kurs-Chatbot", layout="centered")
st.sidebar.title("Sprache / Langue / Lingua")
language_choice = st.sidebar.radio("Choose / Choisir / Scegli", list(languages.keys()))
lang = languages[language_choice]
t = texts[lang]

st.title(t["title"])
st.write(t["intro"])

# Nutzereingaben
selected_language = st.selectbox(t["ask_language"], sorted(set(k["language"] for k in kurse)))
keywords = st.text_input(t["ask_keywords"])
max_duration = st.slider(t["ask_duration"], 1.0, 20.0, 8.0, step=0.5)

# Filtern und Bewerten
def relevance_score(kurs, keywords, max_duration, lang):
    score = 0
    if kurs["language"] != selected_language:
        return 0
    if kurs["duration_hours"] > max_duration:
        return 0
    text = f"{kurs['title']} {kurs['description']} {kurs['category']}".lower()
    for word in keywords.lower().split():
        if word in text:
            score += 2
        elif difflib.get_close_matches(word, text.split(), n=1, cutoff=0.8):
            score += 1
    return score

if keywords:
    ranked = sorted(kurse, key=lambda k: relevance_score(k, keywords, max_duration, lang), reverse=True)
    top_matches = [k for k in ranked if relevance_score(k, keywords, max_duration, lang) > 0][:3]

    if top_matches:
        st.subheader(t["results"])
        for k in top_matches:
            st.markdown(f"### {k['title']}")
            st.markdown(f"- **{k['language']}** | ⏱️ {k['duration_hours']} Std.")
            st.markdown(f"- 👥 {k['target_group']}")
            st.markdown(f"- 🧭 Kategorie: {k['category']}")
            st.markdown(f"- 📝 Beschreibung:

{k['description']}")
            st.markdown("---")
    else:
        st.warning(t["no_results"])
