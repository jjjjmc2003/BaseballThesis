import streamlit as st


# Page title
def show():
    st.title("Decade TSNE Plots (1950-2010)")

    # Brief description
    st.write(
        "In this video the different TSNEs of hitters is displayed, the general idea of this section is to display"
        "just how different the decades are from each other, some share similarities while others do not resemble"
        "the other in the slightest "
    )

    # Embed YouTube video
    st.video("https://youtu.be/n8caodd2ZzA?si=70ldPUJfHY7cNaof")

    st.markdown("### 1950s - Era of Uniformity")
    st.markdown(
        "The 1950s represent baseball's most uniform era. Hitters clustered very tightly together, "
        "showing that most players had similar skill sets — high batting average, low strikeouts, "
        "and very little power. There were almost no outliers. For example, in 1957 and 1958 the "
        "clusters were nearly perfect circles, reflecting a contact-heavy game built around consistency."
    )

    st.markdown("### 1960s - Slow Separation")
    st.markdown(
        "The early 1960s still looked similar to the '50s, but by the late '60s the data began to stretch. "
        "Hitters started to differentiate — some focusing more on power, others on speed. In 1968, "
        "small outlier groups began to form, suggesting the early rise of specialized hitting profiles."
    )

    st.markdown("### 1970s - Rise of Specialization")
    st.markdown(
        "The 1970s saw the cluster spread dramatically. From 1974 to 1977, the projections show "
        "elongated shapes and isolated groups. Power hitters and stolen base threats started to pull away "
        "from the contact-hitting majority, marking a clear evolution in offensive strategy."
    )

    st.markdown("### 1980s - Power-Speed Blend")
    st.markdown(
        "Early 1980s clusters (1981–1983) were very spread out, but compressed again by 1984–1986 — "
        "reflecting a possible league shift towards more balanced hitters. However, the late '80s saw variance explode again. "
        "In 1987 and 1988, extreme outliers reappeared, likely reflecting players with high strikeouts but huge home run numbers."
    )

    st.markdown("### 1990s - Power Revolution")
    st.markdown(
        "The 1990s are where the power era fully arrives. By 1995 and 1997, there are clear, tight outlier clusters "
        "far from the main group — likely representing the PED-era sluggers with record-setting home run rates. "
        "Variance is at its peak as hitters begin fully committing to power profiles."
    )

    st.markdown("### 2000s - Systematic Specialization")
    st.markdown(
        "From 2000 onward, the clusters stabilize but stay heavily separated. Hitters are now trained into "
        "specific roles — high on-base players, speedsters, or pure power hitters. The lower clusters "
        "seen repeatedly in 2003 and 2006 likely represent players with extreme HR/PA numbers, low averages, or high strikeouts."
    )

    st.markdown("### 2010 - The Modern Game")
    st.markdown(
        "By 2010, the hitting landscape looks fully modern. Role-based clustering is obvious — "
        "hitters are no longer generalized but fit specific statistical molds. This reflects a baseball world "
        "heavily shaped by analytics and optimized player development, where every hitter has a clearly defined purpose in a lineup."
    )
