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

# Initialize session state
if "game_state" not in st.session_state:
    st.session_state.game_state = {
        "nickname": None,
        "current_noun": None,
        "remaining_nouns": None,
        "score": 0,
        "trials": 0,
        "total_nouns": 0,
    }

# Function to reset the game state
def reset_game_state():
    st.session_state.game_state = {
        "nickname": None,
        "current_noun": None,
        "remaining_nouns": None,
        "score": 0,
        "trials": 0,
        "total_nouns": 0,
    }

# Function to initialize countable nouns
def initialize_nouns(nickname):
    reset_game_state()
    filtered_df = df_countable.copy()
    if filtered_df.empty:
        st.error("No countable nouns available. Please try again later.")
        return
    st.session_state.game_state["nickname"] = nickname
    st.session_state.game_state["remaining_nouns"] = filtered_df.sample(frac=1).to_dict(orient="records")
    st.session_state.game_state["total_nouns"] = len(filtered_df)
    st.session_state.game_state["current_noun"] = st.session_state.game_state["remaining_nouns"].pop()

# Function to check user's plural input
def check_plural(user_input):
    game_state = st.session_state.game_state
    if not game_state.get("current_noun"):
        st.error("Please click 'Show the Noun' first.")
        return

    correct_plural = game_state["current_noun"]["Plural"].strip().lower()
    game_state["trials"] += 1

    if user_input.lower().strip() == correct_plural:
        game_state["score"] += 1
        feedback = f"✅ Correct! The plural of '{game_state['current_noun']['Word']}' is '{correct_plural}'."
    else:
        feedback = f"❌ Incorrect. The plural of '{game_state['current_noun']['Word']}' is '{correct_plural}'."

    if not game_state["remaining_nouns"]:
        feedback += f" 🎉 Great job, {game_state['nickname']}! All nouns have been answered correctly. (Score: {game_state['score']}/{game_state['total_nouns']})"
        game_state["current_noun"] = None
    else:
        game_state["current_noun"] = game_state["remaining_nouns"].pop()

    return feedback

# Streamlit UI
st.title("NounSmart: Spelling")
st.markdown("Practice the plural forms of words from unit 1 and 2.There are 18 items in total. Try to get all the answers correct.
    Enter a nickname to start.")

# Input for nickname
nickname = st.text_input("Enter your nickname:", key="nickname_input")

if st.button("Start Game"):
    if nickname:
        initialize_nouns(nickname)
    else:
        st.error("Please enter a nickname to start.")

if st.session_state.game_state["current_noun"]:
    st.subheader(f"Current Noun: {st.session_state.game_state['current_noun']['Word']}")
    plural_input = st.text_input("Enter the plural form:")
    if st.button("Check Answer"):
        feedback = check_plural(plural_input)
        st.success(feedback)

if st.session_state.game_state["current_noun"] is None and st.session_state.game_state["total_nouns"] > 0:
    st.markdown(f"🎉 Game over! Final Score: {st.session_state.game_state['score']}/{st.session_state.game_state['total_nouns']}")

