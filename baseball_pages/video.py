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
    st.header("TSNE Through the Years Colored By PA")
    st.video("https://youtu.be/QdGHw5WFNSg")

    st.write(
        "To better understand the TSNE plots seen above these are the same plots only colored by Plate Appearances"
        "in an effort to better display the trends of everyday players and the bench players. With a TSNE it is important"
        "to remember that it does not preserve global orientation. That means that the entire projection can rotate, flip, "
        "or shift between years.With that being said what matters is which shapes emerge, how clusters "
        "expand or contract, and how new groupings appear or vanish over time"
    )

    st.header("Interpretation of Results")

    # 1950s
    st.subheader("1950s: Clarity and Cohesion")
    st.write(
        "The 1950s clusters are compact and tightly grouped, reflecting an era of low variance in player types and output. "
        "Offensive styles were conservative: high contact, low strikeout, low walk rates. In 1955, for instance, the MLB average K% was just 9.4%, "
        "and BB% hovered around 9.5%, indicating consistency in approach. Players shared similar profiles — think Richie Ashburn or Nellie Fox — high BA, low HR."
    )

    # 1960s
    st.subheader("1960s: Tightening and Conformity")
    st.write(
        "In the early '60s, t-SNE projections shrink further, especially 1963–1966, forming a very dense central blob. "
        "This reflects the historically low offensive output during this period. 1968, 'The Year of the Pitcher', is a standout — "
        "league-wide BA fell to .237 and OBP to .299, the lowest in modern history. This compression likely explains the ultra-clustered projection. "
        "The shape suggests the league's hitters were statistically more alike than ever before."
    )

    # 1970s
    st.subheader("1970s: Expansion and Emergence of Outliers")
    st.write(
        "The 1970s display more variance. By 1973, clusters begin to stretch horizontally and form minor separations. "
        "This reflects the introduction of the DH in the AL and the start of true role divergence. For instance, the 1977 season had multiple high-HR, "
        "low-contact sluggers emerge alongside traditional hitters. League OBP also began to diverge more clearly by player archetype."
    )

    # 1980s
    st.subheader("1980s: Dynamic Shifts and Role Differentiation")
    st.write(
        "From 1982 to 1987, the clusters expand and arc downward, indicating new offensive bifurcations. "
        "1983 is a turning point — OBP and BB% start separating. You can see distinct clusters emerge: one for contact hitters like Wade Boggs (low K%, high BB%), "
        "and one for mid-power threats like Dale Murphy (elevated HR/PA, ~5%). These projections reveal a decade increasingly defined by specialization."
    )

    # 1990s
    st.subheader("1990s: Power Surge and Stratification")
    st.write(
        "In 1993 and especially by 1996, projections stretch vertically, indicating offensive stratification. "
        "1998 stands out: MLB average HR/PA hit a peak of 4.1%, and SLG surpassed .420. Players like McGwire and Sosa created statistical outliers. "
        "t-SNE clearly separates power-focused sluggers from average contact hitters. The projection forms a winged shape with bulging lower-left clusters, "
        "which likely correspond to lower OBP, high-K% hitters."
    )

    # 2000s
    st.subheader("2000s: Extremes and Re-balancing")
    st.write(
        "From 2001 to 2006, the visualizations grow more circular again — suggesting re-normalization. "
        "The 2004 plot is more compact again despite the offensive firepower (e.g., Bonds, Pujols). This reflects a balance of extremes: "
        "more hitters with elite OBP (e.g., Bonds’ .609 OBP in 2004), but also a solid average across the league. By 2010, the shape flattens horizontally, "
        "hinting at a league-wide trend toward plate discipline and away from all-or-nothing hitting."
    )

    # Summary bullets
    st.subheader("Summary of Decade Trends")
    st.markdown("""
       - **1950s**: Small compact clusters; low variance in hitter profiles.
       - **1960s**: Most clustered decade; especially 1968 due to offensive suppression.
       - **1970s**: Gradual expansion due to DH rule and expansion teams.
       - **1980s**: Clearer separation of contact vs. power hitters.
       - **1990s**: Largest spread; HR/PA, SLG, and K% caused major statistical divergence.
       - **2000s**: Balanced variance; circular clusters suggest return to equilibrium via improved OBP.
       """)



