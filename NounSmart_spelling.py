import streamlit as st
import pandas as pd

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

# Initialize game state in session state
if "game_state" not in st.session_state:
    st.session_state.game_state = {
        "nickname": None,
        "current_noun": None,
        "remaining_nouns": None,
        "score": 0,
        "trials": 0,
        "total_nouns": 0,
        "answered_correctly": set(),
    }
if "plural_input" not in st.session_state:
    st.session_state.plural_input = ""

# Function to reset the game state
def reset_game_state():
    st.session_state.game_state = {
        "nickname": None,
        "current_noun": None,
        "remaining_nouns": None,
        "score": 0,
        "trials": 0,
        "total_nouns": 0,
        "answered_correctly": set(),
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
    st.session_state.game_state["current_noun"] = None

# Function to show a random noun
def show_random_noun():
    game_state = st.session_state.game_state
    if not game_state["remaining_nouns"]:
        st.success(f"🎉 Great job, {game_state['nickname']}! Final Score: {game_state['score']}/{game_state['total_nouns']}.")
        return None
    game_state["current_noun"] = game_state["remaining_nouns"].pop()
    st.session_state.plural_input = ""  # Clear the input box
    return game_state["current_noun"]["Word"]

# Function to check user's plural input
def check_plural(user_input):
    game_state = st.session_state.game_state
    if not game_state.get("current_noun"):
        return "Please click 'Show the Noun' first."

    correct_plural = game_state["current_noun"]["Plural"].strip().lower()
    game_state["trials"] += 1

    if user_input.lower().strip() == correct_plural:
        if game_state["current_noun"]["Word"] not in game_state["answered_correctly"]:
            game_state["score"] += 1
            game_state["answered_correctly"].add(game_state["current_noun"]["Word"])
        feedback = f"✅ Correct! The plural of '{game_state['current_noun']['Word']}' is '{correct_plural}'. (Score: {game_state['score']}/{game_state['trials']}) Click 'Show the Noun' button to continue."
    else:
        # Add the noun back to the remaining list for retry
        game_state["remaining_nouns"].insert(0, game_state["current_noun"])
        feedback = f"❌ Incorrect. The plural of '{game_state['current_noun']['Word']}' is '{correct_plural}'. (Score: {game_state['score']}/{game_state['trials']}). It will appear again. Click 'Show the Noun' button to continue."

    game_state["current_noun"] = None  # Reset current noun after checking
    return feedback

# Streamlit UI
st.title("NounSmart: Spelling")
st.markdown("""
There are 16 items in total. Try to get all the plural forms correct.
Enter your nickname to start.
""")

# Input for nickname
nickname = st.text_input("Nickname:", key="nickname_input")

if st.button("Start Game"):
    if nickname:
        initialize_nouns(nickname)
        st.success(f"Game started! Good luck, {nickname}!")
    else:
        st.error("Please enter a nickname to start.")

if st.session_state.game_state["remaining_nouns"] is not None:
    if st.button("Show the Noun"):
        noun = show_random_noun()
        if noun:
            st.subheader(f"Current Noun: {noun}")

    if st.session_state.game_state["current_noun"]:
        plural_input = st.text_input("Enter the plural form:", key="plural_input")
        if st.button("Check Answer"):
            feedback = check_plural(plural_input)
            st.success(feedback)

# Final feedback
if st.session_state.game_state["remaining_nouns"] is not None and not st.session_state.game_state["remaining_nouns"]:
    score = st.session_state.game_state["score"]
    trials = st.session_state.game_state["trials"]
    total_nouns = st.session_state.game_state["total_nouns"]

    if score == total_nouns and trials == total_nouns:
        st.markdown(f"🌟 **Perfect score!** Incredible work, {st.session_state.game_state['nickname']}! You got every answer right on the first try! 🌟")
    else:
        st.markdown(f"👏 **Well done, {st.session_state.game_state['nickname']}!** You scored {score}/{trials}. Keep practicing to achieve a perfect score!")




