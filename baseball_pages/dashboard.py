import streamlit as st

def show():
    # Page Title
    st.title("📊 MLB Hitting Evolution Analysis")

    # Introduction Section
    st.markdown("## Project Overview")
    st.write(
        "This project explores how Major League Baseball (MLB) hitting has evolved from **1950 to the present day**. "
        "We aim to uncover the driving forces behind these changes and analyze trends in other aspects of hitting such as"
        " **power hitting vs. contact hitting** "

    )

    # Project Goal Section
    st.markdown("## 🔍 Research Goal")
    st.write(
        "The goal of this study is to **quantify the evolution of hitting styles in MLB** and determine the key factors responsible for these changes. "
        "Specifically, we seek to answer:"
    )

    st.markdown(
        """
        - **How has the distribution of power hitters vs. contact hitters changed over time?**
        - **Are modern hitters more optimized for home runs rather than batting average?**
        - **Has the rise in average fastball velocity affected offensive production?**
        - **What role has advanced training, analytics, and scouting played in shaping modern hitters?**
        """
    )

    # Methodology Section
    st.markdown("## ⚙️ Methodology")
    st.write(
        "To analyze these questions, we leverage **machine learning techniques** on MLB statistical data "
        "from **1950 to the present day**. Our approach includes:"
    )

    st.markdown(
        """
        - **Clustering Analysis**: Grouping hitters by playing style using **PCA (Principal Component Analysis)** and **K-Means Clustering**.
        - **Trend Analysis**: Examining statistical trends in **batting average, home runs, strikeouts, and slugging percentage** over decades.
        - **Velocity Impact Study**: Investigating how **rising pitch velocities** have affected hitters' performance.
        - **ML Models**: Predicting how hitting metrics correlate with **historical changes in training and pitching strategy**.
        """
    )

    # Call to Action
    st.markdown("### 🚀 What's Next?")
    st.write(
        "Explore the other sections of this app to dive deeper into the findings, view **visual insights**, "
        "and watch an explanatory **YouTube video** on the research."
    )
