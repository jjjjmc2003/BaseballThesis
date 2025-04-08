import streamlit as st

def show():
    # Page Title
    st.title("📊 MLB Hitting Evolution Analysis")

    # Introduction Section
    st.markdown("## Project Overview")
    st.write(
        "This thesis investigates how Major League Baseball (MLB) hitters have changed from **1950 to the present day**, "
        "with a focus on how advances in training, increased pitch velocity, and changes in game philosophy have influenced "
        "hitter roles. Using a combination of **machine learning**, **dimensionality reduction**, and **trend analysis**, "
        "we compare decades of hitting data to examine whether the line between **power hitters** and **contact hitters** has blurred."
    )

    # Project Goal Section
    st.markdown("## 🔍 Research Goal")
    st.write(
        "The central aim is to **quantify how hitter profiles and offensive trends have evolved** over time and to determine the "
        "factors that may have driven those shifts. This includes investigating changes in performance, injury risk, and strategic approaches."
    )

    # Methodology Section
    st.markdown("## Features")
    st.write(
        "To explore these questions, we analyze MLB hitting data by decade using both statistical and machine learning techniques:"
    )

    st.markdown(
        """
        - **Clustering & Dimensionality Reduction**: Using **PCA** and **TSNE** to visualize and group hitters and decades by performance metrics
        - **Trend Analysis**: Observing decade-by-decade and yearly changes in **batting average**, **slugging percentage**, **strikeout rate**, etc
        - **Historical and Type Comparison**: Contrasting modern hitters with those from earlier decades to identify evolving archetypes, and contact vs power hitters
        - **Chatbot trained on dataset available to answer all questions baseball or completely unrelated 
        """
    )

    # Call to Action
    st.markdown("### How to Explore?")
    st.write(
        "Use the navigation menu to explore visual dashboards, watch how the TSNE's change over the years, and examine interactive analyses of how "
        "MLB hitters have evolved"
    )
