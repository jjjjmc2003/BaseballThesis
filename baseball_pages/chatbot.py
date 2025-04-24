# import statements
import streamlit as st  # This is the web apps import
import pandas as pd  # for data processing
import os  # used to check if files exist
import re  # for finding years
from openai import OpenAI  # import to use ChatGPT inside our app


def show():  # This function runs the whole chatbot app
    # Add custom styles so our app looks cleaner
    st.markdown("""
        <style>
            .main {background-color: #f8f9fa;}  /* Light background */
            .stTextInput > div > div > input {
                background-color: #ffffff;  /* White text input box */
                border-radius: 8px;  /* Rounded corners */
                padding: 0.75em;  /* Space inside box */
                border: 1px solid #ccc;  /* Light gray border */
            }
        </style>
    """, unsafe_allow_html=True)

    # Show the app's title and short description
    st.markdown("### 💬 Welcome to the **Baseball Stats Chatbot**")
    st.write("Ask anything about MLB hitters from **1950 to 2010** 📊⚾")

    # create a place to store chat history if one not already made
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Try to find CSV data file with player stats
    data = ["data/combined_yearly_stats_all_players.csv"]
    existing_files = [f for f in data if os.path.exists(f)]  # Keep only files that exist

    # If no data file is found, show a warning and stop running
    if not existing_files:
        st.warning("Combined data file not found in the data/ folder.")
        return

    # Try loading the file into a pandas DataFrame
    try:
        df = pd.read_csv(existing_files[0], encoding="ISO-8859-1")
    except Exception as e:
        st.error(f"Error loading data: {e}")  # Show error if loading fails
        return

    # Function that finds all the years (1950–2010) mentioned in a question
    def extract_years_from_question(q):
        return re.findall(r"\b(19[5-9][0-9]|200[0-9]|2010)\b", q)

    # Check if the question is asking about trends or comparisons over time
    def is_broad_question(q):
        q_lower = q.lower()  # make it lowercase so it's easier to match
        keywords = [  # keywords likely to be used in a broad question
            "trend", "change", "over time", "best year", "which year", "what year", "all time",
            "best hitters", "most", "top hitters", "power hitting", "compare decades"
        ]
        # Return True if any of these words or multiple years are found
        return any(phrase in q_lower for phrase in keywords) or len(extract_years_from_question(q)) > 1

    # Make a summary of the stats for each decade
    def summarize_by_decade(df):
        summary = ""
        # Go through each decade from 1950 to 2010
        for decade_start in range(1950, 2010, 10):
            decade_df = df[(df["Year"] >= decade_start) & (df["Year"] < decade_start + 10)]  # Filter for decade
            if not decade_df.empty:
                stats = decade_df.describe().to_string()  # Get stats summary
                summary += f"\n📅 {decade_start}s Summary:\n{stats}\n"
        return summary  # Return all summaries together

    # Make a prompt to send to ChatGPT based on the question and filtered data
    def generate_prompt(question, context_df):
        if is_broad_question(question):  # If question is about multiple years
            summary_text = summarize_by_decade(context_df)  # Use decade summary
        else:
            year_match = extract_years_from_question(question)  # Find specific year
            if year_match:
                year = int(year_match[0])  # Convert year to number
                context_df = context_df[context_df["Year"] == year]  # Filter by that year
            summary_text = context_df.describe(include='all').to_string()  # Show full stats

        # Return a full message to send to ChatGPT
        return f"""You are a baseball analyst trained on MLB data from 1950 to 2010.

Use the following data summary to answer the user's question.

DATA SUMMARY: 
{summary_text}

QUESTION:
{question} 

Answer:"""

    # If there are old questions/answers, show them in an expandable list
    if st.session_state.chat_history:
        st.markdown("### 🗂️ Chat History")
        for i, (q, a) in enumerate(st.session_state.chat_history, 1):
            with st.expander(f"Q{i}: {q}"):  # Click to expand each question
                st.write(a)  # Show the answer

    # Function to turn chat history into plain text
    def get_txt_history():
        if "chat_history" in st.session_state and st.session_state.chat_history:
            return "\n\n".join(
                f"Q{i + 1}: {q}\nA{i + 1}: {a}" for i, (q, a) in enumerate(
                    st.session_state.chat_history))  # get the history and add 1 to the position in the array for the question number
        return "No chat history to export."  # If empty

    # Function to turn chat history into a CSV
    def get_csv_history():
        if "chat_history" in st.session_state and st.session_state.chat_history:
            df_export = pd.DataFrame(st.session_state.chat_history, columns=["Question", "Answer"])
            return df_export.to_csv(index=False).encode("utf-8")  # turn into a csv with 2 columns question and answer
        return "".encode("utf-8")  # Return empty file if no chat

    # Show button to clear the chat history
    if st.session_state.chat_history:
        if st.button("🧹 Clear History"):
            st.session_state.chat_history = []  # Empty it out
            st.rerun()  # Refresh the app

    # Let the user type in a question
    st.write("Note: questions not on dataset say **Outside Knowledge** in question")  # Note to user
    st.markdown("#### 🔍 Type your question below:")
    user_question = st.text_input("",
                                  placeholder="e.g. How did home run rates change over time?")  # placeholder to give user an idea of what to say

    # When the user types a question and presses enter
    if user_question and user_question != st.session_state.get("last_question", ""):
        try:
            # Create an OpenAI client using the secret API key
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

            # If they mention “outside knowledge”, give GPT freedom to use general info
            if "outside knowledge" in user_question.lower():
                prompt = f"""You are a knowledgeable baseball assistant. Please answer the following question using general knowledge and reasoning beyond any specific dataset:

{user_question}

Answer:"""
            else:
                # Otherwise build the prompt based on our dataset
                prompt = generate_prompt(user_question, df)

            # Show loading spinner while we wait
            with st.spinner("Thinking... 💭"):
                # Ask ChatGPT and get the answer
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )

            # Grab the answer from GPT's response
            answer = response.choices[0].message.content
            # Save the question and answer to our chat history
            st.session_state.chat_history.append((user_question, answer))
            st.session_state["last_question"] = user_question

            # Show the answer nicely
            st.markdown("### 🧠 GPT’s Analysis:")
            st.success(answer)

        except Exception as e:
            # If something goes wrong, show an error
            st.error(f"GPT API Error: {e}")

    # If we have chat history, let the user download it
    if "chat_history" in st.session_state and st.session_state.chat_history:
        st.markdown("### 💾 Export Chat History")
        col1, col2 = st.columns(2)  # Two columns for the buttons
        with col1:
            # Download as text
            st.download_button("🔘 Download as .txt", get_txt_history(), "chat_history.txt", "text/plain")
        with col2:
            # Download as excel spreadsheet
            st.download_button("📄 Download as .csv", get_csv_history(), "chat_history.csv", "text/csv")

