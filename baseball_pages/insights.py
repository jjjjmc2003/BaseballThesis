import streamlit as st


def show():
    st.title("Key Insights")

    st.write("### 1. Power vs. Contact Hitters")
    st.write("Power hitters tend to have higher strikeout rates but also more home runs.")

    st.write("### 2. Pitch Velocity Trends")
    st.write("Pitch velocities have increased over the years, possibly leading to a decline in contact hitting.")

    st.write("### 3. Machine Learning Models")
    st.write("By using PCA and clustering, we categorized hitters based on performance trends from 1950 to today.")
