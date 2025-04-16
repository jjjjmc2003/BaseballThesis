import streamlit as st
import pandas as pd
import os
from openai import OpenAI
import re

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
    st.write("**Note**: to ask about anything non baseball related or not related to the dataset prompt it using"
               '\n"Using Knowledge Outside of the Dataset" will help it respond more accurately')


    # Chat History

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


    # Load Historical Data

    decades = [f"data/{decade}stats.csv" for decade in range(1950, 2010, 10)]
    existing_files = [f for f in decades if os.path.exists(f)]

    if not existing_files:
        st.warning("⚠️ No data files found in the 'data/' folder.")
        return

    dataframes = []

    for file in existing_files:
        try:
            # Extract year from filename like "1950stats.csv"
            year = int(os.path.basename(file).split("stats")[0])
            df_year = pd.read_csv(file, encoding="ISO-8859-1")
            df_year["Year"] = year  # Add Year column for filtering
            dataframes.append(df_year)
        except Exception as e:
            st.error(f"❌ Error loading {file}: {e}")
            return  # Only return if a specific file causes a crash

    if not dataframes:
        st.error("❌ No valid dataframes were loaded.")
        return

    df = pd.concat(dataframes, ignore_index=True)

    # Prompt Generator

    def generate_prompt(question, context_df):
        # Optional: auto-detect year from question

        year_match = re.findall(r"\b(19[5-9][0-9]|200[0-9]|2010)\b", question)
        if year_match:
            year = int(year_match[0])
            context_df = context_df[context_df["Year"] == year]
            player_count = context_df["Player"].nunique() if "Player" in context_df.columns else len(context_df)
            extra_summary = f"\nNOTE: There are {player_count} unique players recorded in the {year} season."
        else:
            extra_summary = ""

        # Describe + player count
        stats_summary = context_df.describe(include='all').to_string()
        prompt = f"""You are a baseball analyst bot trained on MLB data from 1950 to 2010. 
        Use the following data summary to answer this question: {question}

        DATA SUMMARY:
        {stats_summary}

        {extra_summary}

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
            # Use GPT's general knowledge if user prompts it
            if "using knowledge outside of the dataset" in user_question.lower():
                prompt = f"""You are a knowledgeable baseball chatbot. Please answer the following question using general baseball knowledge and reasoning beyond any specific dataset:

            {user_question}

            Answer:"""
            else:
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
