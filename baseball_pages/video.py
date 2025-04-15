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

    st.write(
        "This section explores how the statistical makeup of MLB hitters evolved from 1950 through 2010 "
        "using t-SNE visualizations. Each scatterplot represents a dimensionality-reduced projection of "
        "hitters’ offensive profiles from a single season, allowing us to see how player types and hitting "
        "styles clustered and diverged over time."
    )

    st.header("1950s: Clarity and Cohesion")
    st.write(
        "During the early 1950s, the clusters are tightly grouped, with players forming a dense central region. "
        "This reflects a more homogenized style of hitting, likely leaning toward traditional contact-oriented play. "
        "There are very few outliers, indicating that most hitters had very similar offensive profiles. "
        "As the decade progresses, clusters begin to expand slightly, foreshadowing more offensive variety in future decades."
    )

    st.header("1960s: Tightening and Conformity")
    st.write(
        "The 1960s show a trend back toward dense clustering. Especially in the mid-to-late 60s, the data points "
        "are extremely compact. This reflects the 'Pitcher's Era' where offensive performance dropped dramatically. "
        "The 1968 plot in particular is extremely tight, confirming the suppressed offense that led to MLB lowering "
        "the mound in 1969 to boost scoring."
    )

    st.header("1970s: Expansion and Emergence of Outliers")
    st.write(
        "In the 1970s, the clusters begin to stretch horizontally, reflecting greater variance in player profiles. "
        "This is when we start seeing clear separation between player types — more home run hitters, high OBP players, "
        "and aggressive swingers all occupying distinct spaces within the t-SNE plots. "
        "By the late 70s, isolated sub-clusters begin to form, signaling the rise of specialized hitters."
    )

    st.header("1980s: Dynamic Shifts and Role Differentiation")
    st.write(
        "The early 1980s show vertical stacking in the plots — suggesting a wider spread in certain offensive stats "
        "like strikeouts or batting average. From 1982-1984, the clusters flatten horizontally, creating a plane of "
        "diverse hitter profiles. By 1986-1988, the scatter expands further, showing subgroup formations likely "
        "representing power hitters, contact hitters, or OBP specialists."
    )

    st.header("1990s: Power Surge and Stratification")
    st.write(
        "The early 1990s show more fragmentation and separation in the data. As we move into 1993-1995, the plots "
        "begin displaying wide spreads with both dense clusters and extreme outliers. This corresponds to the early "
        "stages of the steroid era where home run rates surged. By 1996-1999, distinct pods of players emerge, "
        "showing a league dominated by power-heavy offensive profiles."
    )

    st.header("2000s: Extremes and Re-balancing")
    st.write(
        "The early 2000s continue the trends from the late 90s — broad spreads, isolated clusters, and clear statistical outliers. "
        "However, from 2004 to 2006, we see the densest formations shift upward, indicating a shift toward more balanced hitting "
        "profiles with fewer extremely low performers. From 2007 to 2010, clusters begin to collapse slightly, reflecting a re-balancing "
        "of offensive profiles likely due to increased regulation and the end of the steroid era."
    )

    st.subheader("Summary of Decade Trends")
    st.write(
        "- 1950s–60s: Homogeneity and suppression of extremes.\n"
        "- 1970s: Gradual expansion and emergence of offensive variety.\n"
        "- 1980s: Rising differentiation and formation of player subtypes.\n"
        "- 1990s: Power era with major statistical outliers.\n"
        "- 2000s: Offensive peaks followed by controlled normalization."
    )


