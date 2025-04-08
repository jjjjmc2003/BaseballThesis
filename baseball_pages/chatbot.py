import streamlit as st
import pandas as pd
import os
from openai import OpenAI

def show():

    # PAGE HEADER + INSTRUCTIONS
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

    st.markdown("### 💬 Welcome to the **Baseball Stats Chatbot**")
    st.write("Ask anything about MLB hitters from **1950 to 2010** 📊⚾")
    st.caption('Note: To ask general baseball questions, include something like "Using outside knowledge" in your prompt.')

    # Chat History
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Load Historical Data
    combined_all = "data/combined_yearly_stats_all_players.csv"

    if not os.path.exists(combined_all):
        st.warning("⚠️ combined_yearly_stats_all_players.csv not found in the 'data/' folder.")
        return

    try:
        df = pd.read_csv(combined_all, encoding="ISO-8859-1")
        st.info("📊 Loaded dataset: All MLB players from 1950–2010.")
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return

    # 🧠 Detect stat-based questions
    def is_data_based_question(question):
        keywords = ["home run", "batting average", "slugging", "strikeout", "HR", "AB", "BA", "SLG", "OPS", "RBI", "AVG", "H", "OBP"]
        return any(keyword.lower() in question.lower() for keyword in keywords)

    # 🧠 Generate Data-Based Prompt
    def generate_prompt(question, context_df):
        import re
        year_matches = re.findall(r"\b(19[5-9][0-9]|200[0-9]|2010)\b", question)
        if year_matches:
            year = int(year_matches[0])
            context_df = context_df[context_df["Year"] == year]

        sample_cols = [col for col in ["Player", "Year", "BA", "AB", "H", "HR", "SLG"] if col in context_df.columns]
        if "BA" in context_df.columns:
            context_df = context_df.sort_values(by="BA", ascending=False).head(10)

        try:
            sample_data = context_df[sample_cols].to_string(index=False)
        except Exception:
            sample_data = "Data could not be sampled due to missing columns."

        prompt = f"""You are a baseball analyst bot trained on MLB player data from 1950–2010. Use the data below to answer this question:

QUESTION:
{question}

DATA:
{sample_data}

Answer:"""

        return prompt

    # Show Chat History
    if st.session_state.chat_history:
        st.markdown("### 🗂️ Chat History")
        for i, (q, a, mode) in enumerate(st.session_state.chat_history[::+1], 1):
            with st.expander(f"Q{i} ({mode}): {q}"):
                st.write(a)

    # Clear Chat Button
    if st.session_state.chat_history:
        if st.button("🧹 Clear History"):
            st.session_state.chat_history = []
            st.rerun()

    # Chat Input
    st.markdown("#### 🔍 Type your question below:")
    user_question = st.text_input("", placeholder="e.g. How did home run rates change over time?")

    # GPT Response
    if user_question:
        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

            if is_data_based_question(user_question):
                prompt = generate_prompt(user_question, df)
                mode = "📊 Data Expert"
            else:
                prompt = f"""You are a knowledgeable baseball historian and analyst. Use your general knowledge to answer this question:

Question: {user_question}

Answer:"""
                mode = "🧠 Baseball Expert"

            with st.spinner("Thinking... 💭"):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )

            answer = response.choices[0].message.content
            st.session_state.chat_history.append((user_question, answer, mode))

            st.markdown(f"### {mode}'s Answer:")
            st.success(answer)

            # Download buttons
            import io

            def get_txt_history():
                history = ""
                for i, (q, a, mode) in enumerate(st.session_state.chat_history, 1):
                    history += f"Q{i} ({mode}): {q}\nA{i}: {a}\n\n"
                return history

            def get_csv_history():
                df = pd.DataFrame(st.session_state.chat_history, columns=["Question", "Answer", "Mode"])
                return df.to_csv(index=False).encode("utf-8")

            st.markdown("### 💾 Export Chat History")
            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    label="🔘 Download as .txt",
                    data=get_txt_history(),
                    file_name="chat_history.txt",
                    mime="text/plain"
                )

            with col2:
                st.download_button(
                    label="📄 Download as .csv",
                    data=get_csv_history(),
                    file_name="chat_history.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"⚠️ GPT API Error: {e}")
