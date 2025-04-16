import streamlit as st
import pandas as pd
import os
import re
from openai import OpenAI

def show():
    # PAGE STYLING
    st.markdown("""
        <style>
            .main {background-color: #f8f9fa;}
            .stTextInput > div > div > input {
                background-color: #ffffff;
                border-radius: 8px;
                padding: 0.75em;
                border: 1px solid #ccc;
            }
        </style>
    """, unsafe_allow_html=True)

    # PAGE HEADER
    st.markdown("### 💬 Welcome to the **Baseball Stats Chatbot**")
    st.write("Ask anything about MLB hitters from **1950 to 2010** 📊⚾")
    st.write("**Note**: To ask about anything non-baseball related or not related to the dataset, prompt it using:\n"
             "**Outside Knowledge** this will help it respond more accurately.")

    # CHAT HISTORY
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # LOAD DATA
    data = ["data/combined_yearly_stats_all_players.csv"]
    existing_files = [f for f in data if os.path.exists(f)]

    if not existing_files:
        st.warning("⚠️ Combined data file not found in the 'data/' folder.")
        return

    try:
        df = pd.read_csv(existing_files[0], encoding="ISO-8859-1")
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return

    # UTILITIES
    def extract_years_from_question(q):
        return re.findall(r"\b(19[5-9][0-9]|200[0-9]|2010)\b", q)

    def is_broad_question(q):
        return ("trend" in q.lower() or "change" in q.lower() or "over time" in q.lower() or
                len(extract_years_from_question(q)) > 1)

    def summarize_by_decade(df):
        summary = ""
        for decade_start in range(1950, 2010, 10):
            decade_df = df[(df["Year"] >= decade_start) & (df["Year"] < decade_start + 10)]
            if not decade_df.empty:
                stats = decade_df.describe().to_string()
                summary += f"\n📅 {decade_start}s Summary:\n{stats}\n"
        return summary

    def generate_prompt(question, context_df):
        if is_broad_question(question):
            summary_text = summarize_by_decade(context_df)
        else:
            year_match = extract_years_from_question(question)
            if year_match:
                year = int(year_match[0])
                context_df = context_df[context_df["Year"] == year]
            summary_text = context_df.describe(include='all').to_string()

        return f"""You are a baseball analyst trained on MLB data from 1950 to 2010.

Use the following data summary to answer the user's question.

DATA SUMMARY:
{summary_text}

QUESTION:
{question}

Answer:"""

    # CHAT HISTORY DISPLAY
    if st.session_state.chat_history:
        st.markdown("### 🗂️ Chat History")
        for i, (q, a) in enumerate(st.session_state.chat_history, 1):
            with st.expander(f"Q{i}: {q}"):
                st.write(a)

    # ALWAYS SHOW EXPORT BUTTONS IF HISTORY EXISTS
    if st.session_state.chat_history:
        def get_txt_history():
            return "\n\n".join(f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(st.session_state.chat_history))

        def get_csv_history():
            df_export = pd.DataFrame(st.session_state.chat_history, columns=["Question", "Answer"])
            return df_export.to_csv(index=False).encode("utf-8")


    # CLEAR CHAT BUTTON
    if st.session_state.chat_history:
        if st.button("🧹 Clear History"):
            st.session_state.chat_history = []
            st.rerun()

    # CHAT INPUT
    st.markdown("#### 🔍 Type your question below:")
    st.caption("Note: questions not on dataset say **Outside Knowledge** in question")
    user_question = st.text_input("", placeholder="e.g. How did home run rates change over time?")

    # HANDLE INPUT
    if user_question:
        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

            # Decide prompt type
            if "outside knowledge" in user_question.lower():
                prompt = f"""You are a knowledgeable baseball assistant. Please answer the following question using general knowledge and reasoning beyond any specific dataset:

{user_question}

Answer:"""
            else:
                prompt = generate_prompt(user_question, df)

            # Get GPT response
            with st.spinner("Thinking... 💭"):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )

            answer = response.choices[0].message.content
            st.session_state.chat_history.append((user_question, answer))

            # Display
            st.markdown("### 🧠 GPT’s Analysis:")
            st.success(answer)

        except Exception as e:
            st.error(f"⚠️ GPT API Error: {e}")

    st.markdown("### 💾 Export Chat History")
    col1, col2 = st.columns(2)

    with col1:
        st.download_button("🔘 Download as .txt", get_txt_history(), "chat_history.txt", "text/plain")

    with col2:
        st.download_button("📄 Download as .csv", get_csv_history(), "chat_history.csv", "text/csv")
