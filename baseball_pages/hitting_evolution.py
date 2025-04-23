def show():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import os
    import matplotlib.pyplot as plt
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from matplotlib.lines import Line2D

    st.title("Hitting Evolution (1950–2010)")

    # --- Setup ---
    DATA_DIR = "data"
    decades = ["1950", "1960", "1970", "1980", "1990", "2000", "2010"]
    files = [f"{decade}stats.csv" for decade in decades]
    full_years_file = os.path.join(DATA_DIR, "combined_yearly_stats_all_players.csv")

    # --- Load decade data ---
    decade_data = {}
    for file in files:
        path = os.path.join(DATA_DIR, file)
        if os.path.exists(path):
            df = pd.read_csv(path, encoding="ISO-8859-1")
            df.columns = df.columns.str.strip()
            decade_data[file[:4]] = df

    key_stats = ["BA", "OBP", "SLG", "HR", "SO", "BB", "PA"]
    decade_avg = {}
    for decade, df in decade_data.items():
        df = df[key_stats].copy()
        df.rename(columns={"SO": "K"}, inplace=True)
        df["HR/PA"] = df["HR"] / df["PA"]
        df["K%"] = df["K"] / df["PA"]
        df["BB%"] = df["BB"] / df["PA"]
        decade_avg[decade] = df.mean()
    summary_stats_avg = pd.DataFrame(decade_avg).T

    # --- PCA on decade data ---
    scaler = StandardScaler()
    pca_features = ["BA", "OBP", "SLG", "HR/PA", "K%", "BB%"]
    scaled = scaler.fit_transform(summary_stats_avg[pca_features])
    pca = PCA(n_components=2)
    decade_pca_scores = pca.fit_transform(scaled)
    decade_pca_df = pd.DataFrame(decade_pca_scores, columns=["PC1", "PC2"], index=summary_stats_avg.index)

    # PCA Decades
    st.header("Decade-Based PCA of Hitting Trends")
    fig, ax = plt.subplots()
    ax.scatter(decade_pca_df["PC1"], decade_pca_df["PC2"], color="blue")
    for i, txt in enumerate(decade_pca_df.index):
        ax.annotate(txt, (decade_pca_df["PC1"][i], decade_pca_df["PC2"][i]))
    ax.set_xlabel("Principal Component 1 (Contact Component)")
    ax.set_ylabel("Principal Component 2 (Power Component)")
    ax.set_title("PCA Analysis of Decade Seasons (Contact vs Power)")
    st.pyplot(fig)
    st.markdown(f"**Explained Variance:** PC1: {pca.explained_variance_ratio_[0]*100:.2f}%, "
                f"PC2: {pca.explained_variance_ratio_[1]*100:.2f}%")

    st.markdown("""**Interpretation:**  
        This PCA visualization shows the shifting offensive identity of Major League Baseball from every decade 
        season. In 1950, hitters prioritized contact, walks, and avoiding strikeouts, a small ball
         era where the goal was to simply get on base and move runners. As the 60s and 70s rolled in, 
         the MLB entered what's now known as the “Pitcher’s Era,” where strikeout rates rose and offense 
         plummeted. That trend pushed MLB to lower the mound in 1969, a moment that fundamentally reshaped 
         hitting. These shifts are visible in the PCA, as the season 1960 and 1970 are stationed
          in the bottom left meaning low contact and power. As time progressed so did hitting as the
          year 1980 had revived the contact game and even put up decent power numbers noticeable by
          their position on the PCA. 1990 continued this trend in power but dropped to a more average contact 
          position. However, in 2000, the Steroid Era was in full effect, and the season average shifts 
          sharply upward in power, reinforcing what is already known, the early 2000s were built on slugging.
    """)

    #PCA Feature Contributions
    loadings = pd.DataFrame(pca.components_.T, index=pca_features, columns=["PC1", "PC2"])
    fig_load, ax_load = plt.subplots(figsize=(10, 5))
    loadings.plot(kind='bar', ax=ax_load)
    ax_load.set_title("PCA Feature Contributions to PC1 and PC2")
    ax_load.set_ylabel("Contribution Magnitude")
    ax_load.set_xlabel("Hitting Metrics")
    st.pyplot(fig_load)
    st.dataframe(loadings.style.format("{:.2f}"))

    st.markdown("""**PCA Weight Interpretation:**  
    - PC1 strongly weights OBP and BB% positively and strikeouts negatively,  lining up with the traits of contact
     hitting.  
    - PC2 heavily loads strikeouts, SLG and HR/PA while also adding walking as a negative. This perfectly
     captures the traits of power hitting. Furthermore, these components help us separate high-discipline 
     contact hitting from the free-swinging sluggers and categorize the years based on their preferred 
     offensive approach or tendency.
    """)

    # load dataset and stats
    if os.path.exists(full_years_file):
        full_df = pd.read_csv(full_years_file, encoding="ISO-8859-1")
        full_df.columns = full_df.columns.str.strip()
        full_df["HR/PA"] = full_df["HR"] / full_df["PA"]
        full_df["K%"] = full_df["SO"] / full_df["PA"]
        full_df["BB%"] = full_df["BB"] / full_df["PA"]

        year_grouped = full_df.groupby("Year")[pca_features].mean().dropna()
        projected_scaled = scaler.transform(year_grouped)
        year_scores = pca.transform(projected_scaled)
        year_pca_df = pd.DataFrame(year_scores, columns=["PC1", "PC2"], index=year_grouped.index)

        # Color map
        def get_decade_color(year):
            if 1950 <= year < 1960: return 'black'
            elif 1960 <= year < 1970: return 'blue'
            elif 1970 <= year < 1980: return 'green'
            elif 1980 <= year < 1990: return 'red'
            elif 1990 <= year < 2000: return 'purple'
            elif 2000 <= year < 2010: return 'brown'
            elif 2010 <= year <= 2019: return 'magenta'
            return 'gray'

        # Year-by-Year PCA
        st.header("Year-by-Year Contact vs Power PCA")
        fig2, ax2 = plt.subplots()
        for year in year_pca_df.index:
            color = get_decade_color(year)
            label_color = 'red' if year % 10 == 0 else 'black'
            ax2.scatter(year_pca_df.loc[year, "PC1"], year_pca_df.loc[year, "PC2"], color=color)
            ax2.annotate(str(year), (year_pca_df.loc[year, "PC1"], year_pca_df.loc[year, "PC2"]), fontsize=7, color=label_color)
        ax2.set_xlabel("Principal Component 1 (Contact Component)")
        ax2.set_ylabel("Principal Component 2 (Power Component)")
        ax2.set_title("Yearly PCA of MLB Hitting (Contact vs Power)")

        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='1950s', markerfacecolor='black'),
            Line2D([0], [0], marker='o', color='w', label='1960s', markerfacecolor='blue'),
            Line2D([0], [0], marker='o', color='w', label='1970s', markerfacecolor='green'),
            Line2D([0], [0], marker='o', color='w', label='1980s', markerfacecolor='red'),
            Line2D([0], [0], marker='o', color='w', label='1990s', markerfacecolor='purple'),
            Line2D([0], [0], marker='o', color='w', label='2000s', markerfacecolor='brown'),
            Line2D([0], [0], marker='o', color='w', label='2010s', markerfacecolor='magenta')
        ]
        ax2.legend(handles=legend_elements, title="Decade")
        st.pyplot(fig2)

        st.markdown("""**Interpretation:**  
        This chart zooms in from decades to individual seasons, and the story gets even more interesting. 
        The 1950s seasons group neatly on the high contact side of the PCA, with OBP and BB% holding strong.
         As the 60s and 70s unfold, we see the visual decline in offense, as strikeouts rise and hits 
         disappear, a direct result of dominant pitching. The dip is obvious and supported by rule changes
          like the lowering of the mound. In the 80s there was a shift back to more average to a bit above average
          hitting as both contact and power hover around the origin. However, by the late 90s and early 2000s, 
          things shift dramatically. The cluster of points moves sharply into the power heavy half of the plot, 
          coinciding with the explosion of
            home run records and slugging statistics during the Steroid Era. In the late 2000s, the graph 
            begins to hint at a new phase, still powerful, but beginning to stabilize in terms of contact, 
            most likely due to the crackdown on steroids by the MLB after 2004 and the new power driven hitting
            mindset.
        """)

        # Plot PCA loadings for Year-by-Year PCA
        loadings = pca.components_
        feature_names = pca_features
        loadings_df = pd.DataFrame(loadings.T, columns=["PC1", "PC2"], index=feature_names)


        fig_weights, ax_weights = plt.subplots(figsize=(10, 6))
        loadings_df.plot(kind='bar', ax=ax_weights)
        ax_weights.set_title("PCA Feature Contributions to PC1 and PC2")
        ax_weights.set_ylabel("Contribution Magnitude")
        ax_weights.set_xlabel("Hitting Metrics")
        st.pyplot(fig_weights)
        st.dataframe(loadings_df.style.format("{:.2f}"))

        # Write-up for PCA interpretation
        st.markdown(
            "**Interpretation:** As you may have noticed the weights are the same as it is the exact same"
            " PCA just with all the years added to it. I simply included the weights to prove this. Furthermore,"
            ' this PCA just as above uses PC1 to measure statistics generally associated with a contact hitter'
            ' such as high walk rates, high on base percentage, and low strikeout rates lining up with the traits'
            ' of a contact hitter. While PC2 measure power output as it is positively effected by HR/PA,or home '
            ' runs per plate appearance, slugging percentage, and striking out while walking is negative. '
            ' These line up nicely with the traits of a power hitter.')

        # --- Clustering ---
        st.header("Clustered Year by Year PCA")
        kmeans = KMeans(n_clusters=4, random_state=42)
        year_pca_df["Cluster"] = kmeans.fit_predict(year_pca_df[["PC1", "PC2"]])
        fig3, ax3 = plt.subplots()
        for cluster in sorted(year_pca_df["Cluster"].unique()):
            subset = year_pca_df[year_pca_df["Cluster"] == cluster]
            ax3.scatter(subset["PC1"], subset["PC2"], label=f"Cluster {cluster}")
            for year in subset.index:
                ax3.annotate(str(year), (subset.loc[year, "PC1"], subset.loc[year, "PC2"]), fontsize=7)
        ax3.set_title("KMeans Clustering of Yearly Hitting PCA (Contact vs Power)")
        ax3.set_xlabel("Principal Component 1 (Contact Component)")
        ax3.set_ylabel("Principal Component 2 (Power Component)")
        ax3.legend()
        st.pyplot(fig3)

        # --- Cluster descriptions ---
        st.write("**Cluster Averages:**")
        full_with_years = full_df.groupby("Year")[pca_features].mean().dropna()
        full_with_years["Cluster"] = year_pca_df["Cluster"]
        st.dataframe(full_with_years.groupby("Cluster").mean().style.format("{:.3f}"))

        st.markdown("""**Interpretation:**  
        Each cluster groups years with similar hitting profiles. For example, one group may include seasons 
        with high HR/PA and K%, while another favors OBP and low K%. These clusters highlight changing 
        offensive priorities across eras. Cluster 0 highlights the low parts of contact and power which 
        means that output productivity in those years are at lows in both power and contact hitting. Signifying
        low offensive output in those years, also evident from on average that cluster having the worst offensive
        production in almost every category, except for strikeouts which is not a good thing to lead in. 
        In Cluster 1, based off the positioning on the PCA and stats driving that location it is a high 
        contact and average to high power cluster. To no surprise the stats listed above demonstrate that 
        Cluster 1 is the leader in almost every category making it by far the best all around hitting cluster.
        Cluster 2 reflects a contact oriented approach, leading statistically in BB% or walk percentage and 
        having the lowest percentage of strikeouts or K% meaning this group made a lot of contact and walked a 
        lot identifying them perfectly with contact styled hitting. Cluster 3 demonstrates classic power hitting
        approaches, average to low contact with high power output. This is backed up both by the positioning on 
        the PCA but also the stats as they are tied with Cluster 1 in terms of Homeruns per Plate Appearance and 
        are a close second behind Cluster 0 for highest strikeout rate, demonstrating a low contact approach and 
        high power approach. Furthermore, demonstrate how the eras changed and how different seasons in this time
        frame correlate with the other statistically.  
        """)

        # Trend Line Through Years
        st.header("Trend Line of Year by Year PCA")
        st.write("Every 5 years labeled")
        fig4, ax4 = plt.subplots()
        ax4.plot(year_pca_df["PC1"], year_pca_df["PC2"], color='yellow', label = 'Trend Line')
        ax4.scatter(year_pca_df["PC1"], year_pca_df["PC2"], color='gray', label = 'Seasons')
        for year in year_pca_df.index:
            if year % 5 == 0:
                ax4.annotate(str(year), (year_pca_df.loc[year, "PC1"], year_pca_df.loc[year, "PC2"]), fontsize=10, color="blue")
        ax4.set_xlabel("Principal Component 1 (Contact Component)")
        ax4.set_ylabel("Principal Component 2 (Power Component)")
        ax4.set_title("Trend Line of Yearly Hitting PCA (Contact vs Power)")
        ax4.legend()
        st.pyplot(fig4)

        # --- Apply smoothing to PC1 and PC2 ---
        st.header("\n\nSmoothed Trend Line of Year by Year Hitting PCA (Contact vs Power)")
        st.write("Only every 5 years shown, projected directly onto the smoothed path")

        # --- Define smoothing ---
        def smooth_series(series, window_size=5):
            n = len(series)
            smoothed = np.zeros(n)
            for i in range(n):
                indices = list(range(max(0, i - 2), min(n, i + 3)))
                smoothed[i] = np.mean([series[j] for j in indices])
            return smoothed

        # --- Smooth PC1 and PC2 ---
        years = year_pca_df.index.tolist()
        pc1 = year_pca_df["PC1"].values
        pc2 = year_pca_df["PC2"].values

        smoothed_pc1 = smooth_series(pc1)
        smoothed_pc2 = smooth_series(pc2)

        # --- Get positions of every 5th year ---
        projection_years = [year for year in years if year % 5 == 0]
        projection_coords = []

        for proj_year in projection_years:
            i = years.index(proj_year)
            x = smoothed_pc1[i]
            y = smoothed_pc2[i]
            projection_coords.append((x, y, proj_year))

        # --- Plot smoothed line and projections only ---
        fig5, ax5 = plt.subplots(figsize=(8, 6))
        ax5.plot(smoothed_pc1, smoothed_pc2, color='orange', linewidth=2, label='Smoothed Trend Line')

        # Label projected years only
        for x, y, year in projection_coords:
            ax5.scatter(x, y, color='blue', s=40)
            ax5.annotate(str(year), (x, y), fontsize=10, color='blue')

        ax5.set_xlabel("Principal Component 1 (Contact Component)")
        ax5.set_ylabel("Principal Component 2 (Power Component)")
        ax5.set_title("Smoothed Trend Line of Yearly Hitting PCA (Contact vs Power)")
        ax5.legend(["Smoothed Trend Line"])
        st.pyplot(fig5)

        st.markdown("""**Interpretation:**  
        The trajectory line shows a clear directional evolution from high contact/low power years in the 1950s
         to the more power-oriented years in the 90s 2000s and 2010s. The path reinforces the impact of the
          lowering the mound, Steroid Era, training styles, and increasing power based offensive approach.
        """)

        st.header("Conclusion")
        st.write("This PCA story captures the full evolution of MLB offense from 1950 to 2010. Starting "
                 "in the 1950s, we see a league built on pure contact, with hitters focused on getting on"
                 " base and avoiding strikeouts. In this era, power was rare and consistency at the plate"
                 " was everything. That trend slowly changed through the 1960s and 70s, often referred to"
                 ' as the "pitcher era." During these years, offensive output declined so sharply that'
                ' by 1969, MLB made the decision to lower the mound, hoping to bring '
                'back balance between pitchers and hitters.That shift is captured'
                 ' in the PCA plot, as 1960, 1970, and many of the years in between, sit '
                 'far down and to the left of the PCA. This reflects the low contact and low power output. '
                 'This decline isn’t just visual, it’s statistical. Cluster 0, where these seasons '
                 'reside, has the lowest batting average, OBP, and slugging percentage of any group. '
                 'These were tough years to hit. Then, the 1980s arrive, and we begin to see '
                 'a noticeable climb in both power and contact. This was the rise of more complete'
                 ' hitters, players who could do a bit of everything. Offenses had adapted to the '
                 'lowered mound, and lineups became deeper. Cluster 2 picks up many of these years, and'
                 ' it’s easy to see why. This group leads in walk rate and has the lowest strikeout rate, '
                 'representing a classic contact-heavy era with solid OBP across the board. But the real '
                 'spike comes in the late 90s and 2000s, where the PCA and clustering both make it obvious.'
                 ' This was the height of the Steroid Era. HR/PA jumped, slugging surged, and strikeouts '
                 'rose with it. The game shifted to a three true outcomes model: home runs, walks, and '
                 'strikeouts. Cluster 3 captures this transformation, moderate contact, high power, and '
                 'very little plate discipline. And at the very peak, you find Cluster 1, which represents'
                 ' the most offensively productive years across the board — high BA, high OBP, high SLG,'
                 ' and balanced plate discipline. These weren’t just juiced hitters, these were the peak '
                 'years of overall output. By the late 2000s, 2010 in the decade plot, the trend line pulls'
                 ' back slightly. Power remains, '
                 'but contact drops, and walks begin to decline again. Stricter PED testing, a new '
                 'generation of pitchers, and the rise of advanced analytics start changing the offensive'
                 ' approach once again. Hitters become more data driven, chasing launch angles and '
                 'exit velocity before those terms even entered the mainstream. This transition is '
                 'captured in the yellow trajectory line, a chaotic path from low contact '
                 'eras to a peak in the 90s-2000s, and a slow decline towards a sole power hitting approach.'
                 ' Altogether, the PCA plots, clusters, and trajectory reveal a story that isn’t just about'
                 ' stats. It’s about how rules changed, how training evolved, and how the identity of the'
                 ' hitter transformed. From choking up on the bat to swinging for the fences, MLB offense '
                 'was ever changing and this data shows how it evolved.')
