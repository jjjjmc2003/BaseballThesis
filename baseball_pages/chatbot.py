import streamlit as st
import pandas as pd
import os
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

    st.markdown("### 💬 Welcome to the **Baseball Stats Chatbot**")
    st.write("Ask anything about MLB hitters from **1950 to 2010** 📊⚾")
    st.caption('This chatbot uses both the dataset and general baseball knowledge to answer your questions.')

    # Chat History
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Load Dataset
    combined_all = "data/combined_yearly_stats_all_players.csv"

    if not os.path.exists(combined_all):
        st.warning("⚠️ combined_yearly_stats_all_players.csv not found in the 'data/' folder.")
        return

    try:
        df = pd.read_csv(combined_all, encoding="ISO-8859-1")
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
        df = df.dropna(subset=["Year"])
        df["Year"] = df["Year"].astype(int)
        st.info("📊 Loaded dataset: All MLB players from 1950–2010.")
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return

    # Generate Dataset-Based Prompt
    def generate_dataset_prompt(question, context_df):
        sample_cols = [col for col in ["Player", "Year", "BA", "AB", "H", "HR", "SLG"] if col in context_df.columns]
        try:
            sample_data = context_df[sample_cols].sort_values(by="BA", ascending=False).head(10).to_string(index=False)
        except Exception:
            sample_data = "Not enough data available for preview."

        return f"""You are a baseball analyst bot trained only on MLB hitter stats from 1950–2010. Use the data below to answer the question using statistical reasoning only.

QUESTION:
{question}

DATA:
{sample_data}

Answer:"""

    # Show Chat History
    if st.session_state.chat_history:
        st.markdown("### 🗂️ Chat History")
        for i, (q, dataset_answer, gpt_answer) in enumerate(st.session_state.chat_history, 1):
            with st.expander(f"Q{i}: {q}"):
                st.markdown("#### Dataset-Based Response:")
                st.write(dataset_answer)
                st.markdown("#### GPT Response:")
                st.write(gpt_answer)

    # Clear History Button
    if st.session_state.chat_history:
        if st.button("🧹 Clear History"):
            st.session_state.chat_history = []
            st.rerun()

    # Chat Input
    st.markdown("#### 🔍 Type your question below:")
    user_question = st.text_input("", placeholder="e.g. How many home runs were hit in 1985?")

    # GPT Responses
    if user_question:
        try:
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

            # Build prompts
            dataset_prompt = generate_dataset_prompt(user_question, df)
            general_prompt = f"""You are a knowledgeable baseball expert. Use your broad understanding of the sport to answer the following question:

QUESTION:
{user_question}

Answer:"""

            # Run both prompts
            with st.spinner("Thinking... 💭"):
                dataset_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": dataset_prompt}]
                )

                gpt_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": general_prompt}]
                )

            dataset_answer = dataset_response.choices[0].message.content
            gpt_answer = gpt_response.choices[0].message.content

            # Save chat history
            st.session_state.chat_history.append((user_question, dataset_answer, gpt_answer))

            # Display answers
            st.markdown("### Dataset-Based Response:")
            st.success(dataset_answer)

            st.markdown("### GPT Response:")
            st.info(gpt_answer)

            # Export chat history
            def get_txt_history():
                history = ""
                for i, (q, a1, a2) in enumerate(st.session_state.chat_history, 1):
                    history += f"Q{i}: {q}\nDataset-Based Response:\n{a1}\n\nGPT Response:\n{a2}\n\n"
                return history

            def get_csv_history():
                return pd.DataFrame(
                    st.session_state.chat_history,
                    columns=["Question", "Dataset-Based Response", "GPT Response"]
                ).to_csv(index=False).encode("utf-8")

            st.markdown("### 💾 Export Chat History")
            col1, col2 = st.columns(2)

            with col1:
                st.download_button("🔘 Download as .txt", get_txt_history(), "chat_history.txt", "text/plain")

            with col2:
                st.download_button("📄 Download as .csv", get_csv_history(), "chat_history.csv", "text/csv")

        except Exception as e:
            st.error(f"⚠️ GPT API Error: {e}")
