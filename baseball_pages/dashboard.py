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

    st.markdown(
        """
        ### Key Questions:
        - **Have power hitters become more dominant while contact hitters have declined?**
        - **Do modern hitters focus more on exit velocity and launch angle than batting average?**
        - **Is there a correlation between rising fastball velocity and changes in offensive outcomes—or injury rates?**
        - **What role has sports science and analytics played in reshaping hitter development and success?**
        """
    )

    # Methodology Section
    st.markdown("## ⚙️ Methodology")
    st.write(
        "To explore these questions, we analyze MLB hitting data by decade using both statistical and machine learning techniques:"
    )

    st.markdown(
        """
        - **Clustering & Dimensionality Reduction**: Using **PCA** and **TSNE** to visualize and group hitters by performance metrics.
        - **Trend Analysis**: Observing decade-by-decade changes in **batting average**, **slugging percentage**, **strikeout rate**, and **home run rate**.
        - **Velocity Correlation Study**: Linking increasing average **pitch velocities** to hitter performance and possible injury trends.
        - **Historical Comparison**: Contrasting modern hitters with those from earlier decades to identify evolving archetypes.
        """
    )

    # Call to Action
    st.markdown("### 🚀 What's Next?")
    st.write(
        "Use the navigation menu to explore visual dashboards, watch our **explanatory video**, and examine interactive analyses of how "
        "MLB hitters have evolved in response to the modern game’s demands."
    )
