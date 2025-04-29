import streamlit as st

def show():
    # Page Title
    st.title("⚾Hitting Evolution Dashboard⚾")

    # Project overview
    st.markdown("## Project Overview")
    st.write(
        "This thesis investigates how Major League Baseball (MLB) hitters have changed from **1950 to the present day**, "
        "with a focus on how advances in training, increased pitch velocity, and changes in game philosophy have influenced "
        "hitter roles. Using a combination of **machine learning**, **dimensionality reduction**, and **trend analysis**, "
        "we compare decades of hitting data to examine whether the line between **power hitters** and **contact hitters** has blurred."
        '\n\n\n\n\n\n\n\n\n\n\n'
        "*All Data is sourced from **Baseball Reference** and the Chatbot uses Open AI's **GPT-3.5** model to answer questions about the data."
    )

    st.markdown("## Research Goal") #Research Goals
    st.write(
        "The central aim is to **quantify how hitter profiles and offensive trends have evolved** over time and to determine the "
        "factors that may have driven those shifts. This includes investigating changes in performance, strategic approaches, and ."
    )


    st.markdown("## Features") #Features of project
    st.write(
        "To explore these questions, we analyze MLB hitting data by decade using both statistical and"
        " machine learning techniques:"
    )
        #The features
    st.markdown(
        """
        - **Clustering & Dimensionality Reduction**: Using **PCA** and **TSNE** to visualize and group
         hitters and decades by performance metrics
        \n
        - **Trend Analysis**: Observing decade-by-decade and yearly changes in **batting average**, 
        **slugging percentage**, **strikeout rate**, etc
        \n
        - **Historical and Type Comparison**: Contrasting modern hitters with those from earlier decades to
         identify evolving archetypes, and contact vs power hitters
        \n
        - **Chatbot**: trained on dataset available to answer all questions baseball or completely unrelated 
        """
    )


    st.markdown("## How to Explore?") #Navigation directions
    st.write(
        "Use the navigation menu to the left to explore the web app"
    )
