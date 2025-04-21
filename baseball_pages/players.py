import streamlit as st
import pandas as pd
import numpy as np
import os
import requests
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler


def show():
    st.title("Players (Power vs Contact)")

    st.write("Note on the Player Names: * - bats left-handed, # - bats both (switch hitter),\n nothing - bats right")

    # ------------------------------------------------------------------ SET‑UP
    DATA_DIR = "data"
    os.makedirs(DATA_DIR, exist_ok=True)
    GITHUB_REPO = "https://raw.githubusercontent.com/jjjjmc2003/BaseballThesis/main/data/"
    decades = ["1950", "1960", "1970", "1980", "1990", "2000", "2010"]
    files = [f"{d}stats.csv" for d in decades]
    YEARLY_CSV = "combined_yearly_stats_all_players.csv"

    def download_file(fname: str):
        url = f"{GITHUB_REPO}{fname}"
        dest = os.path.join(DATA_DIR, fname)
        if not os.path.exists(dest):
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                with open(dest, "wb") as f:
                    f.write(r.content)

    # decade files
    for f in files:
        download_file(f)
    # yearly file
    download_file(YEARLY_CSV)

    # ---------------------------------------------------------- LOAD DECADE DF
    @st.cache_data
    def load_data():
        data = {}
        for f in files:
            df = pd.read_csv(os.path.join(DATA_DIR, f), encoding="ISO-8859-1")
            df.columns = df.columns.str.strip()
            data[f.split("stats")[0]] = df
        return data

    data = load_data()

    # --------------------------------------------------------------- PREP PLAYERS
    key_stats = ["BA", "OBP", "HR", "SO", "BB", "PA", "SLG", "Player", "AB"]
    frames = []
    for decade, df in data.items():
        if not set(key_stats).issubset(df.columns):
            continue
        df = df[key_stats].copy()
        df.rename(columns={"SO": "K"}, inplace=True)
        df["HR/PA"] = df["HR"] / df["PA"]
        df["K%"]    = df["K"]  / df["PA"]
        df["BB%"]   = df["BB"] / df["PA"]
        df["ISO"]   = df["SLG"] - df["BA"]
        df["Decade"] = int(decade)
        frames.append(df)

    player_df = pd.concat(frames, ignore_index=True)
    player_df.dropna(subset=["BA", "OBP", "K%", "BB%", "ISO", "HR/PA"], inplace=True)


    # ---------------------------------------------------------- SCALE SCORES
    scaler = MinMaxScaler()
    cols_to_scale = ["BA", "OBP", "K%", "BB%", "ISO", "HR/PA"]
    player_df[cols_to_scale] = scaler.fit_transform(player_df[cols_to_scale])
    player_df["K%"] = 1 - player_df["K%"]     # invert K%

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
    # --- global medians for a power veto
    iso_med = player_df["ISO"].median()
    hrpa_med = player_df["HR/PA"].median()

    c75, c50 = player_df["ContactScore"].quantile([.75, .50])
    p75, p50 = player_df["PowerScore"].quantile([.75, .50])

    player_df["Hitter Type"] = "Balanced"

    # power specialist
    player_df.loc[
        (player_df["PowerScore"] > p75) &
        (player_df["ContactScore"] <= c50),
        "Hitter Type"
    ] = "Power Hitter"

    # contact specialist  ➜ needs high ContactScore *and* mediocre power numbers
    player_df.loc[
        (player_df["ContactScore"] > c75) &
        (player_df["PowerScore"] <= p50) &
        (player_df["ISO"] <= iso_med) &
        (player_df["HR/PA"] <= hrpa_med),
        "Hitter Type"
    ] = "Contact Hitter"

    # ---------------------------------------------------- THRESHOLDS & LABELS
    c_thresh = player_df["ContactScore"].quantile(0.75)
    p_thresh = player_df["PowerScore"].quantile(0.75)

    player_df["Hitter Type"] = "Balanced"
    player_df.loc[player_df["PowerScore"] > p_thresh, "Hitter Type"] = "Power Hitter"
    player_df.loc[(player_df["ContactScore"] > c_thresh) &
                  (player_df["PowerScore"] <= p_thresh), "Hitter Type"] = "Contact Hitter"

    # ---------------------------------------------------------------- COMPARE
    st.subheader("Compare a Power Hitter and a Contact Hitter")
    power_pool   = player_df[player_df["Hitter Type"] == "Power Hitter"]["Player"].unique()
    contact_pool = player_df[player_df["Hitter Type"] == "Contact Hitter"]["Player"].unique()

    # fallback if bucket is empty
    if power_pool.size == 0:
        power_pool = player_df.nlargest(10, "PowerScore")["Player"].values
    if contact_pool.size == 0:
        contact_pool = player_df.nlargest(10, "ContactScore")["Player"].values

    power_pick = st.selectbox("Select Power Hitter", sorted(power_pool))
    contact_pick = st.selectbox("Select Contact Hitter", sorted(contact_pool))

    stats = ["BA", "OBP", "ISO", "HR/PA", "K%", "BB%"]
    p_stats = player_df[player_df["Player"] == power_pick].iloc[0]
    c_stats = player_df[player_df["Player"] == contact_pick].iloc[0]

    compare = pd.DataFrame({
        "Stat": stats,
        power_pick:  [p_stats[s] for s in stats],
        contact_pick:[c_stats[s] for s in stats]
    })
    st.table(compare)

    # ------------------------------------------------------ GLOBAL SCATTER
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

    # ----------------------------------------------------- DECADE DRILL‑DOWN
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

    st.markdown(f"### Example Power Hitters in {selected_decade}")
    st.dataframe(decade_df[decade_df["Hitter Type"] == "Power Hitter"].head(10))

    st.markdown(f"### Example Contact Hitters in {selected_decade}")
    st.dataframe(decade_df[decade_df["Hitter Type"] == "Contact Hitter"].head(10))

    # ----------------------------------------------------- LOAD YEARLY CSV
    @st.cache_data
    def load_yearly():
        fp = os.path.join(DATA_DIR, YEARLY_CSV)
        if not os.path.exists(fp):
            return pd.DataFrame()
        df = pd.read_csv(fp, encoding="ISO-8859-1")
        df.columns = df.columns.str.strip()

        df["HR/PA"] = df["HR"] / df["PA"]
        df["K%"]    = df["SO"] / df["AB"]
        df["BB%"]   = df["BB"] / df["PA"]
        df["ISO"]   = df["SLG"] - df["BA"]

        scaled = scaler.transform(df[cols_to_scale])
        scaled = pd.DataFrame(scaled, columns=cols_to_scale, index=df.index)
        scaled["K%"] = 1 - scaled["K%"]
        df[cols_to_scale] = scaled

        df["ContactScore"] = (
              0.4*df["BA"] + 0.4*df["OBP"] + 0.1*df["BB%"] + 0.1*df["K%"]
        )
        df["PowerScore"] = (
              0.5*df["ISO"] + 0.5*df["HR/PA"]
        )
        df["Hitter Type"] = "Balanced"
        df.loc[df["PowerScore"] > p_thresh, "Hitter Type"] = "Power Hitter"
        df.loc[(df["ContactScore"] > c_thresh) &
               (df["PowerScore"] <= p_thresh), "Hitter Type"] = "Contact Hitter"
        return df

    yearly_df = load_yearly()

    # ------------------------------------------------ SEASON SLIDER VIEW
    if not yearly_df.empty:
        st.subheader("Season‑by‑Season Contact vs Power (1950‑2010)")
        season = st.slider("Select season", 1950, 2010, 1950)
        season_df = yearly_df[yearly_df["Year"] == season]

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

        st.markdown(f"### Example Power Hitters – {season}")
        st.dataframe(season_df[season_df["Hitter Type"] == "Power Hitter"]
                     .head(10))

        st.markdown(f"### Example Contact Hitters – {season}")
        st.dataframe(season_df[season_df["Hitter Type"] == "Contact Hitter"]
                     .head(10))

        # --- quick console dump -------------------------------------------------------
        # ── Full name lists on‑screen ────────────────────────────────────────────
    st.subheader("Full Lists of Classified Hitters")

    # pull unique, alphabetised arrays
    power_names = sorted(player_df.loc[player_df["Hitter Type"] == "Power Hitter",
    "Player"].unique())
    contact_names = sorted(player_df.loc[player_df["Hitter Type"] == "Contact Hitter",
    "Player"].unique())

    # two side‑by‑side columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔴 Power Hitters")
        # show as scrollable list
        st.dataframe(pd.DataFrame({"Power Hitter": power_names}))

    with col2:
        st.markdown("#### 🔵 Contact Hitters")
        st.dataframe(pd.DataFrame({"Contact Hitter": contact_names}))

    # ----------------------------------------------------- EXPLANATION
    st.markdown("""
### 🧠  How Contact & Power Scores Are Calculated
*Contact Score* rewards high **BA**, high **OBP**, good plate discipline (**BB %**) and low strike‑outs (**K %**).  
*Power Score* rewards **ISO** and **HR/PA** in equal measure.

*Top 25 % on one axis* earns the specialist label provided the player is **not** also elite on the other axis.

Everything else = **Balanced**.
""")
