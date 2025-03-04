import streamlit as st

# Page title
def show():
    st.title("My Thesis on Baseball Stats & Machine Learning")

# Brief description
    st.write(
      "This project explores how baseball statistics have evolved over time, analyzing power hitters, contact hitters, and the impact of increasing pitch velocities using machine learning techniques."
    )

    # Embed YouTube video
    st.video("https://youtu.be/QTlPt20pQaU")
    # Additional content
    st.write("If you're interested in the data science behind baseball analytics, check out my full research below!")

    st.markdown("### Key Insights")
    st.write("- Analyzing historical MLB data to classify hitters into power vs. contact roles")
    st.write("- Clustering MLB hitters by playing era (1950-present) using machine learning")
    st.write("- Investigating the relationship between pitch velocity and hitter success")

    st.markdown("#### **Want to learn more?**")
    st.write("Feel free to reach out or check my other work!")