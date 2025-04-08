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

    try:
        # Use ISO-8859-1 in case of weird characters
        df = pd.concat([pd.read_csv(file, encoding="ISO-8859-1") for file in existing_files], ignore_index=True)
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return


    # Prompt Generator

    def generate_prompt(question, context_df):
        stats_summary = context_df.describe(include='all').to_string()
        prompt = f"""You are a baseball analyst bot trained on MLB data from 1950 to 2010. 
Use the following data summary to answer this question: {question}

DATA SUMMARY:
{stats_summary}

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
