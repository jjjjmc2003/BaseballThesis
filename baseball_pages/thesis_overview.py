import streamlit as st

def show():
    st.title("Thesis Overview")
    st.write(
        "This project explores how baseball statistics have evolved over time, analyzing power hitters, contact hitters, and the impact of increasing pitch velocities using machine learning."
    )
    st.markdown("### Key Areas of Research")
    st.write("- Clustering MLB hitters by playing era")
    st.write("- Machine learning techniques for hitter classification")
    st.write("- Impact of rising pitch velocities on hitter performance")
