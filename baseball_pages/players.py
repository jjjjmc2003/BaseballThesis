import streamlit as st
import pandas as pd
import os
import requests
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import seaborn as sns

def show():
    st.title("Players (Power vs Contact)")

    st.write("Note on the Player Names: * - bats left-handed, # - bats  (switch hitter), nothing - bats right,"
               " ? - unknown")

    # Set up local data directory
    DATA_DIR = "data"
    os.makedirs(DATA_DIR, exist_ok=True)  # Create the data directory if it doesn't exist

    # GitHub Raw File Path
    GITHUB_REPO = "https://raw.githubusercontent.com/jjjjmc2003/BaseballThesis/main/data/"
    decades = ["1950", "1960", "1970", "1980", "1990", "2000", "2010"]
    files = [f"{decade}stats.csv" for decade in decades]

    # Function to download missing files
    def download_file(file_name):
        url = f"{GITHUB_REPO}{file_name}"
        local_path = os.path.join(DATA_DIR, file_name)

        if not os.path.exists(local_path):  # Check if file is already downloaded
            try:
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    with open(local_path, "wb") as f:
                        f.write(response.content)
                    st.success(f"✅ Downloaded: {file_name}")
                else:
                    st.error(f"❌ Error downloading {file_name} (HTTP {response.status_code})")
            except Exception as e:
                st.error(f"❌ Failed to download {file_name}: {e}")

    # Download all missing CSVs
    for file in files:
        download_file(file)

    # Load Data from Local Files
    @st.cache_data
    def load_data():
        data = {}
        for file in files:
            file_path = os.path.join(DATA_DIR, file)
            try:
                df = pd.read_csv(file_path, encoding="ISO-8859-1")
                df.columns = df.columns.str.strip()
                data[file.split("stats")[0]] = df  # Use decade as key
            except Exception as e:
                st.error(f"❌ Error loading {file}: {e}")
        return data

    data = load_data()

    # Process Data for Clustering
    def process_data(data):
        key_stats = ["BA", "OBP", "SLG", "HR", "SO", "BB", "PA"]
        player_data = []

        for decade, df in data.items():
            df.columns = df.columns.str.strip()
            missing_cols = [col for col in key_stats if col not in df.columns]
            if missing_cols:
                st.warning(f"⚠️ Warning: Missing columns in {decade}: {missing_cols}")
                continue

            df = df[key_stats + ["Player"]].copy()
            df.rename(columns={"SO": "K"}, inplace=True)

            # **Calculate Key Rate Stats**
            df["HR/PA"] = df["HR"] / df["PA"]
            df["K%"] = df["K"] / df["PA"]
            df["BB%"] = df["BB"] / df["PA"]
            df["ISO"] = df["SLG"] - df["BA"]  # Isolated Power (ISO)

            df["Decade"] = int(decade)  # Assign decade for reference
            player_data.append(df)

        return pd.concat(player_data, ignore_index=True)

    player_data = process_data(data)

    # Ensure only valid numerical columns are used for PCA & Clustering
    cluster_features = ["BA", "OBP", "SLG", "HR/PA", "K%", "BB%", "ISO"]
    player_data_cleaned = player_data.dropna(subset=cluster_features)

    # **Scale Data for PCA**
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(player_data_cleaned[cluster_features])

    # **Perform PCA**
    pca = PCA(n_components=2)
    pca_transformed = pca.fit_transform(scaled_features)
    player_data_cleaned["PC1"] = pca_transformed[:, 0]
    player_data_cleaned["PC2"] = pca_transformed[:, 1]

    # **Apply Improved Filtering**
    power_hitters = player_data_cleaned.query("HR/PA > 0.04 or ISO > 0.140")
    contact_hitters = player_data_cleaned.query("BA >= 0.270 and OBP >= 0.330 and SLG < 0.450")

    player_data_cleaned["Hitter Type"] = "Balanced"
    player_data_cleaned.loc[power_hitters.index, "Hitter Type"] = "Power Hitter"
    player_data_cleaned.loc[contact_hitters.index, "Hitter Type"] = "Contact Hitter"

    # **Player vs. Player Comparison**
    st.subheader("Compare a Power Hitter vs. a Contact Hitter")
    power_player = st.selectbox("Select a Power Hitter:", power_hitters["Player"].unique())
    contact_player = st.selectbox("Select a Contact Hitter:", contact_hitters["Player"].unique())

    power_stats = power_hitters[power_hitters["Player"] == power_player].iloc[0]
    contact_stats = contact_hitters[contact_hitters["Player"] == contact_player].iloc[0]

    comparison_df = pd.DataFrame({
        "Stat": ["BA", "OBP", "SLG", "HR/PA", "K%", "BB%"],
        power_player: [power_stats["BA"], power_stats["OBP"], power_stats["SLG"], power_stats["HR/PA"], power_stats["K%"], power_stats["BB%"]],
        contact_player: [contact_stats["BA"], contact_stats["OBP"], contact_stats["SLG"], contact_stats["HR/PA"], contact_stats["K%"], contact_stats["BB%"]]
    })

    st.table(comparison_df)

    # **PCA Feature Contribution Plot**
    def plot_pca_feature_contributions():
        """Plots the contributions of features to PC1 and PC2."""
        loadings_df = pd.DataFrame(pca.components_, columns=cluster_features, index=["PC1", "PC2"])

        fig, ax = plt.subplots(figsize=(10, 6))
        loadings_df.T.plot(kind="bar", ax=ax, width=0.8)

        ax.set_title("PCA Feature Contributions to PC1 and PC2")
        ax.set_ylabel("Contribution Magnitude")
        ax.set_xlabel("Hitting Metrics")
        ax.legend(title="Principal Components")
        plt.xticks(rotation=45, ha='right')

        # Display explained variance
        st.write(f"**Explained Variance:** PC1: {pca.explained_variance_ratio_[0] * 100:.2f}%, PC2: {pca.explained_variance_ratio_[1] * 100:.2f}%")

        st.pyplot(fig)

    plot_pca_feature_contributions()

    # **Decade-by-Decade Clustering Study**
    st.subheader("Hitter Clustering Trends Over Time")
    selected_decade = st.selectbox("Select a Decade:", decades)
    decade_data = player_data_cleaned[player_data_cleaned["Decade"] == int(selected_decade)]

    # **Plot Clustering by Decade**
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = {"Power Hitter": "red", "Contact Hitter": "blue", "Balanced": "gray"}

    for hitter_type, color in colors.items():
        subset = decade_data[decade_data["Hitter Type"] == hitter_type]
        ax.scatter(subset["PC1"], subset["PC2"], color=color, label=hitter_type, alpha=0.6)

    ax.set_xlabel("Principal Component 1 (Power Metrics)")
    ax.set_ylabel("Principal Component 2 (Contact/Discipline)")
    ax.set_title(f"Hitter Clustering in {selected_decade}")
    ax.legend()

    st.pyplot(fig)

    # **Show Example Hitters for Selected Decade**
    st.write(f"### Example Power Hitters in {selected_decade}:")
    st.dataframe(decade_data[decade_data["Hitter Type"] == "Power Hitter"].head(10))

    st.write(f"### Example Contact Hitters in {selected_decade}:")
    st.dataframe(decade_data[decade_data["Hitter Type"] == "Contact Hitter"].head(10))
