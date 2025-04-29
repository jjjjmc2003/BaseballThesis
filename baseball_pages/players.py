import streamlit as st #import webapp
import pandas as pd # for data processing
import numpy as np  # for numerical operations
import os # for file path operations
import requests # for downloading files
import matplotlib.pyplot as plt # for plotting
from sklearn.preprocessing import MinMaxScaler # for scaling data


def show():
    # Set the title of the Streamlit app
    st.title("Players (Power vs Contact)")

    # Display a note about player name annotations
    st.write("Note on the Player Names: * - bats left-handed, # - bats both (switch hitter),\n nothing - bats right")

    # Define the data directory and GitHub repository URL
    DATA_DIR = "data"
    os.makedirs(DATA_DIR, exist_ok=True)  # Create the data directory if it doesn't exist
    GITHUB_REPO = "https://raw.githubusercontent.com/jjjjmc2003/BaseballThesis/main/data/"
    decades = ["1950", "1960", "1970", "1980", "1990", "2000", "2010"]
    files = [f"{d}stats.csv" for d in decades] # List of decade files
    YEARLY_CSV = "combined_yearly_stats_all_players.csv"

    # Function to download a file if it doesn't already exist locally
    def download_file(fname: str):
        url = f"{GITHUB_REPO}{fname}"
        dest = os.path.join(DATA_DIR, fname)
        if not os.path.exists(dest):
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                with open(dest, "wb") as f:
                    f.write(r.content)

    # Download decade files
    for f in files:
        download_file(f)
    # Download yearly file
    download_file(YEARLY_CSV)

    # Function to load data from CSV files and cache the result
    @st.cache_data
    def load_data():
        data = {}
        for f in files:
            df = pd.read_csv(os.path.join(DATA_DIR, f), encoding="ISO-8859-1")
            df.columns = df.columns.str.strip()  # Strip whitespace from column names
            data[f.split("stats")[0]] = df  # Use decade as the key
        return data

    # Load the data
    data = load_data()

    # Define key statistics to extract
    key_stats = ["BA", "OBP", "HR", "SO", "BB", "PA", "SLG", "Player", "AB"]
    frames = []
    for decade, df in data.items():
        if not set(key_stats).issubset(df.columns):  # Skip if key stats are missing
            continue
        df = df[key_stats].copy()
        df.rename(columns={"SO": "K"}, inplace=True)  # Rename "SO" to "K"
        # Calculate additional metrics
        df["HR/PA"] = df["HR"] / df["PA"]
        df["K%"]    = df["K"]  / df["PA"]
        df["BB%"]   = df["BB"] / df["PA"]
        df["ISO"]   = df["SLG"] - df["BA"]
        df["Decade"] = int(decade)  # Add decade as a column
        frames.append(df)

    # Combine all decades into a single DataFrame
    player_df = pd.concat(frames, ignore_index=True)
    player_df.dropna(subset=["BA", "OBP", "K%", "BB%", "ISO", "HR/PA"], inplace=True)

    # Scale the data using MinMaxScaler
    scaler = MinMaxScaler()
    cols_to_scale = ["BA", "OBP", "K%", "BB%", "ISO", "HR/PA"]
    player_df[cols_to_scale] = scaler.fit_transform(player_df[cols_to_scale])
    player_df["K%"] = 1 - player_df["K%"]  # Invert K% for better interpretation

    # Calculate ContactScore and PowerScore
    player_df["ContactScore"] = (
          0.4 * player_df["BA"]  +
          0.4 * player_df["OBP"] +
          0.1 * player_df["BB%"] +
          0.1 * player_df["K%"]
    )
    player_df["PowerScore"] = (
          0.5 * player_df["ISO"]   +
          0.5 * player_df["HR/PA"]
    )

    # Calculate global medians for ISO and HR/PA
    iso_med = player_df["ISO"].median()
    hrpa_med = player_df["HR/PA"].median()

    # Calculate thresholds for ContactScore and PowerScore
    c75, c50 = player_df["ContactScore"].quantile([.75, .50])
    p75, p50 = player_df["PowerScore"].quantile([.75, .50])

    # Initialize all players as "Balanced"
    player_df["Hitter Type"] = "Balanced"

    # Label power specialists
    player_df.loc[
        (player_df["PowerScore"] > p75) &
        (player_df["ContactScore"] <= c50),
        "Hitter Type"
    ] = "Power Hitter"

    # Label contact specialists
    player_df.loc[
        (player_df["ContactScore"] > c75) &
        (player_df["PowerScore"] <= p50) &
        (player_df["ISO"] <= iso_med) &
        (player_df["HR/PA"] <= hrpa_med),
        "Hitter Type"
    ] = "Contact Hitter"

    # Recalculate thresholds for labeling
    c_thresh = player_df["ContactScore"].quantile(0.75)
    p_thresh = player_df["PowerScore"].quantile(0.75)

    # Reassign hitter types based on thresholds
    player_df["Hitter Type"] = "Balanced"
    player_df.loc[player_df["PowerScore"] > p_thresh, "Hitter Type"] = "Power Hitter"
    player_df.loc[(player_df["ContactScore"] > c_thresh) &
                  (player_df["PowerScore"] <= p_thresh), "Hitter Type"] = "Contact Hitter"

    # Allow users to compare a power hitter and a contact hitter
    st.subheader("Compare a Power Hitter and a Contact Hitter")
    player_df["K%"] = 1 - player_df["K%"]  # Revert K% for display
    power_pool   = player_df[player_df["Hitter Type"] == "Power Hitter"]["Player"].unique()
    contact_pool = player_df[player_df["Hitter Type"] == "Contact Hitter"]["Player"].unique()

    # Fallback if no players are available in a category
    if power_pool.size == 0:
        power_pool = player_df.nlargest(10, "PowerScore")["Player"].values
    if contact_pool.size == 0:
        contact_pool = player_df.nlargest(10, "ContactScore")["Player"].values

    # Dropdowns for selecting players
    power_pick = st.selectbox("Select Power Hitter", sorted(power_pool))
    contact_pick = st.selectbox("Select Contact Hitter", sorted(contact_pool))

    # Display comparison table
    stats = ["BA", "OBP", "ISO", "HR/PA", "K%", "BB%"]
    p_stats = player_df[player_df["Player"] == power_pick].iloc[0]
    c_stats = player_df[player_df["Player"] == contact_pick].iloc[0]

    compare = pd.DataFrame({
        "Stat": stats,
        power_pick:  [p_stats[s] for s in stats],
        contact_pick:[c_stats[s] for s in stats]
    })
    st.table(compare)

    # Scatter plot for hitter distribution
    st.subheader("Contact vs Power Hitter Distribution (1950‑2010)")
    fig, ax = plt.subplots(figsize=(8, 6))
    palette = {"Power Hitter":"red","Contact Hitter":"blue","Balanced":"gray"}
    for lbl, col in palette.items():
        sub = player_df[player_df["Hitter Type"] == lbl]
        ax.scatter(sub["ContactScore"], sub["PowerScore"],
                   c=col, label=lbl, alpha=.6)
    ax.set_xlabel("Contact Score")
    ax.set_ylabel("Power Score")
    ax.set_title("Hitter Classification Based on Statistical Profile")
    ax.legend()
    st.pyplot(fig)

    # Decade breakdown scatter plot
    st.subheader("Hitter Breakdown by Decade")
    selected_decade = st.selectbox("Select a Decade", decades)
    decade_df = player_df[player_df["Decade"] == int(selected_decade)]

    fig2, ax2 = plt.subplots(figsize=(8, 6))
    for lbl, col in palette.items():
        sub = decade_df[decade_df["Hitter Type"] == lbl]
        ax2.scatter(sub["ContactScore"], sub["PowerScore"],
                    c=col, label=lbl, alpha=.6)
    ax2.set_xlabel("Contact Score")
    ax2.set_ylabel("Power Score")
    ax2.set_title(f"Hitter Clustering in {selected_decade}")
    ax2.legend()
    st.pyplot(fig2)

    # Display example hitters for the selected decade
    st.markdown(f"### Example Power Hitters in {selected_decade}")
    st.dataframe(decade_df[decade_df["Hitter Type"] == "Power Hitter"].head(10))

    st.markdown(f"### Example Contact Hitters in {selected_decade}")
    st.dataframe(decade_df[decade_df["Hitter Type"] == "Contact Hitter"].head(10))

    # Function to load yearly data
    @st.cache_data
    def load_yearly():
        fp = os.path.join(DATA_DIR, YEARLY_CSV)
        if not os.path.exists(fp):
            return pd.DataFrame()
        df = pd.read_csv(fp, encoding="ISO-8859-1")
        df.columns = df.columns.str.strip()

        # Calculate additional metrics
        df["HR/PA"] = df["HR"] / df["PA"]
        df["K%"]    = df["SO"] / df["AB"]
        df["BB%"]   = df["BB"] / df["PA"]
        df["ISO"]   = df["SLG"] - df["BA"]

        # Scale the data
        scaled = scaler.transform(df[cols_to_scale])
        scaled = pd.DataFrame(scaled, columns=cols_to_scale, index=df.index)
        scaled["K%"] = 1 - scaled["K%"]
        df[cols_to_scale] = scaled

        # Calculate ContactScore and PowerScore
        df["ContactScore"] = (
              0.4*df["BA"] + 0.4*df["OBP"] + 0.1*df["BB%"] + 0.1*df["K%"]
        )
        df["PowerScore"] = (
              0.5*df["ISO"] + 0.5*df["HR/PA"]
        )
        # Assign hitter types
        df["Hitter Type"] = "Balanced"
        df.loc[df["PowerScore"] > p_thresh, "Hitter Type"] = "Power Hitter"
        df.loc[(df["ContactScore"] > c_thresh) &
               (df["PowerScore"] <= p_thresh), "Hitter Type"] = "Contact Hitter"
        return df

    # Load yearly data
    yearly_df = load_yearly()

    # Slider for selecting a season
    if not yearly_df.empty:
        st.subheader("Season‑by‑Season Contact vs Power (1950‑2010)")
        season = st.slider("Select season", 1950, 2010, 1950)
        season_df = yearly_df[yearly_df["Year"] == season]

        # Scatter plot for the selected season
        fig_season, ax_season = plt.subplots(figsize=(8, 6))
        for lbl, col in palette.items():
            sub = season_df[season_df["Hitter Type"] == lbl]
            ax_season.scatter(sub["ContactScore"], sub["PowerScore"],
                              c=col, label=lbl, alpha=.6)
        ax_season.set_xlabel("Contact Score")
        ax_season.set_ylabel("Power Score")
        ax_season.set_title(f"Hitter Classification – {season}")
        ax_season.legend()
        st.pyplot(fig_season)

        # Display example hitters for the selected season
        st.markdown(f"### Example Power Hitters – {season}")
        st.dataframe(season_df[season_df["Hitter Type"] == "Power Hitter"]
                     .head(10))

        st.markdown(f"### Example Contact Hitters – {season}")
        st.dataframe(season_df[season_df["Hitter Type"] == "Contact Hitter"]
                     .head(10))

    # Full name lists on-screen
    st.subheader("Full Lists of Classified Hitters")

    # Pull unique, alphabetized arrays
    power_names = sorted(player_df.loc[player_df["Hitter Type"] == "Power Hitter",
    "Player"].unique())
    contact_names = sorted(player_df.loc[player_df["Hitter Type"] == "Contact Hitter",
    "Player"].unique())

    # Two side-by-side columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔴 Power Hitters")
        # Show as scrollable list
        st.dataframe(pd.DataFrame({"Power Hitter": power_names}))

    with col2:
        st.markdown("#### 🔵 Contact Hitters")
        st.dataframe(pd.DataFrame({"Contact Hitter": contact_names}))

    # Explanation of how scores are calculated
    st.markdown("""
### How Contact & Power Scores Are Calculated
*Contact Score* rewards high **BA**, high **OBP**, good plate discipline (**BB %**) and low strike‑outs (**K %**).
*Power Score* rewards **ISO** and **HR/PA** in equal measure.

*Top 25% on one axis* earns the specialist label provided the player is not also elite on the other axis, in which case they are classified 
as power. Think Barry Bonds, all time home run leader greatest power hitter of all time, but also a great contact hitter as he walked a lot 
and had a high batting average. However, since Bonds was so good at both, and being good at power is rare, he is classified as a power hitter.

Everything else = **Balanced**.
""")