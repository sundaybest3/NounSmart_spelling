import streamlit as st
import pandas as pd
import random

# Load the CSV file
csv_url = "https://raw.githubusercontent.com/sundaybest3/NounSmart_spelling/main/nouns_CE_visang.csv"
df = pd.read_csv(csv_url)

# Inspect the columns
expected_columns = ["Page", "Word", "Countability", "Plural"]
missing_columns = [col for col in expected_columns if col not in df.columns]
if missing_columns:
    st.error(f"The following required columns are missing in the CSV: {', '.join(missing_columns)}")
    st.stop()

# Filter only countable nouns
df_countable = df[df["Countability"].str.lower() == "countable"].copy()

# Initialize game state
if "game_state" not in st.session_state:
    st.session_state["game_state"] = {
        "nickname": None,
        "current_noun": None,
        "remaining_nouns": None,
        "score": 0,
        "trials": 0,
        "total_nouns": 0
    }

def reset_game_state():
    st.session_state["game_state"] = {
        "nickname": None,
        "current_noun": None,
        "remaining_nouns": None,
        "score": 0,
        "trials": 0,
        "total_nouns": 0
    }

def initialize_nouns():
    reset_game_state()
    filtered_df = df_countable.copy()
    if filtered_df.empty:
        st.error("No countable nouns available. Please try again later.")
        return
    st.session_state["game_state"]["remaining_nouns"] = filtered_df.sample(frac=1).to_dict(orient="records")
    st.session_state["game_state"]["total_nouns"] = len(filtered_df)

def show_random_noun():
    if not st.session_state["game_state"]["remaining_nouns"]:
        return f"🎉 Great job, {st.session_state['game_state']['nickname']}! All nouns have been answered correctly. (Score: {st.session_state['game_state']['score']}/{st.session_state['game_state']['total_nouns']})"

    st.session_state["game_state"]["current_noun"] = st.session_state["game_state"]["remaining_nouns"].pop()
    return st.session_state["game_state"]["current_noun"]["Word"]

def check_plural(user_input):
    if not st.session_state["game_state"].get("current_noun"):
        return "Please click 'Show the Noun' first."

    correct_plural = st.session_state["game_state"]["current_noun"]["Plural"].strip().lower()
    st.session_state["game_state"]["trials"] += 1

    if user_input.lower().strip() == correct_plural:
        st.session_state["game_state"]["score"] += 1
        feedback = f"✅ Correct! The plural of '{st.session_state['game_state']['current_noun']['Word']}' is '{correct_plural}' (Score: {st.session_state['game_state']['score']}/{st.session_state['game_state']['trials']})."
    else:
        # Add the noun back to the remaining list for retry
        st.session_state["game_state"]["remaining_nouns"].insert(0, st.session_state["game_state"]["current_noun"])
        feedback = f"❌ Incorrect. The plural of '{st.session_state['game_state']['current_noun']['Word']}' is '{correct_plural}' (Score: {st.session_state['game_state']['score']}/{st.session_state['game_state']['trials']}). It will appear again."

    if not st.session_state["game_state"]["remaining_nouns"]:
        feedback += f" 🎉 Great job, {st.session_state['game_state']['nickname']}! All nouns have been answered correctly."

    return feedback

# Streamlit app interface
st.title("NounSmart: Spelling")

if not st.session_state["game_state"]["nickname"]:
    st.session_state["game_state"]["nickname"] = st.text_input("Enter your nickname:", key="nickname")
    if st.button("Start Game"):
        initialize_nouns()
else:
    st.write(f"Welcome, {st.session_state['game_state']['nickname']}!")

    if st.session_state["game_state"]["remaining_nouns"] is None:
        initialize_nouns()

    noun_display = st.session_state["game_state"].get("current_noun", {}).get("Word", "")
    if noun_display:
        st.markdown(f"### Current Noun: {noun_display}")
    else:
        st.markdown("### Current Noun: (None)")

    if st.button("Show the Noun"):
        noun_display = show_random_noun()
        st.markdown(f"### Current Noun: {noun_display}")

    plural_input = st.text_input("Enter the plural form:", key="plural_input")

    if st.button("Check the Answer"):
        feedback = check_plural(plural_input)
        st.write(feedback)

    st.write(f"Score: {st.session_state['game_state']['score']}/{st.session_state['game_state']['trials']} (Total Nouns: {st.session_state['game_state']['total_nouns']})")
