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
    st.caption('Note to prompt the Chatbot to answer a question using outside knowledge (not just statistical data)'
               ' of dataset type "Using information outside of the dataset" then type your question')


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

    # Prompt Generator

    def generate_prompt(question, context_df):
        # Try to extract year if it's mentioned in the question
        import re
        year_matches = re.findall(r"\b(19[5-9][0-9]|200[0-9]|2010)\b", question)
        if year_matches:
            year = int(year_matches[0])
            context_df = context_df[context_df["Year"] == year]

        # Sample a few top hitters by BA or H (limit to avoid overloading tokens)
        sample_cols = ["Player", "Year", "BA", "AB", "H", "HR", "SLG"]  # Adjust to match your columns
        if "BA" in context_df.columns:
            context_df = context_df.sort_values(by="BA", ascending=False).head(10)

        sample_data = context_df[sample_cols].to_string(index=False)

        prompt = f"""You are a baseball analyst bot trained on MLB player data from 1950-2010. Use the data below to answer this question:

    QUESTION:
    {question}

    DATA:
    {sample_data}

    Answer:"""

        return prompt

    #Chat History

    if st.session_state.chat_history:
        st.markdown("### 🗂️ Chat History")
        for i, (q, a) in enumerate(st.session_state.chat_history[::+1], 1):
            with st.expander(f"Q{i}: {q}"):
                st.write(a)


    # Clear Chat Button

    if st.session_state.chat_history != []:
        if st.button("🧹 Clear History"):
            st.session_state.chat_history = []
            st.rerun()


    # Chat Input
    st.markdown("#### 🔍 Type your question below:")
    user_question = st.text_input("", placeholder="e.g. How did home run rates change over time?")


    # GPT Response

    if user_question:
        try:
            # Initialize OpenAI client using Streamlit secrets
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

            # Generate prompt with stats summary
            prompt = generate_prompt(user_question, df)

            # Show spinner while GPT thinks
            with st.spinner("Thinking... 💭"):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )

            # Save and display response
            answer = response.choices[0].message.content
            st.session_state.chat_history.append((user_question, answer))
            st.markdown("### 🧠 GPT’s Analysis:")
            st.success(answer)

            # -------------------------------
            # 💾 Export Chat History
            # -------------------------------
            import io

            if st.session_state.chat_history:
                st.markdown("### 💾 Export Chat History")

                # Convert chat history to plain text
                def get_txt_history():
                    history = ""
                    for i, (q, a) in enumerate(st.session_state.chat_history, 1):
                        history += f"Q{i}: {q}\nA{i}: {a}\n\n"
                    return history

                # Convert chat history to CSV
                def get_csv_history():
                    df = pd.DataFrame(st.session_state.chat_history, columns=["Question", "Answer"])
                    return df.to_csv(index=False).encode("utf-8")

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
