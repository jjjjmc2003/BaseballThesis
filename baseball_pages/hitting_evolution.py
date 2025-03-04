import streamlit as st
import pandas as pd
import os
import requests
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def show():
    st.title("Hitting Evolution (1950-2010)")

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

    # Show confirmation message
    if data:
        st.write("✅ Successfully loaded all available data!")

    # Process Data
    def process_data(data):
        key_stats = ["BA", "OBP", "SLG", "HR", "SO", "BB", "PA"]
        processed_avg = {}
        for decade, df in data.items():
            df.columns = df.columns.str.strip()
            missing_cols = [col for col in key_stats if col not in df.columns]
            if missing_cols:
                st.warning(f"⚠️ Warning: Missing columns in {decade}: {missing_cols}")
                continue
            df = df[key_stats].copy()
            df.rename(columns={"SO": "K"}, inplace=True)
            df["HR/PA"] = df["HR"] / df["PA"]
            df["K%"] = df["K"] / df["PA"]
            df["BB%"] = df["BB"] / df["PA"]
            processed_avg[decade] = df.mean()
        return pd.DataFrame(processed_avg)

    summary_stats_avg = process_data(data)

    # PCA Analysis
    def perform_pca(data):
        numerical_data = data.dropna(axis=1).T  # Drop NaN values and transpose
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numerical_data)
        pca = PCA(n_components=2)
        pca.fit(scaled_data)
        explained_variance = pca.explained_variance_ratio_
        loadings = pca.components_
        return pca.transform(scaled_data), explained_variance, loadings, numerical_data.columns

    if not summary_stats_avg.empty:
        pca_results, variance, loadings, feature_names = perform_pca(summary_stats_avg)
        pca_df = pd.DataFrame(pca_results, columns=["PC1", "PC2"], index=summary_stats_avg.columns)

        # PCA Scatter Plot
        fig, ax = plt.subplots()
        ax.scatter(pca_df["PC1"], pca_df["PC2"], color="blue")
        for i, txt in enumerate(pca_df.index):
            ax.annotate(txt, (pca_df["PC1"][i], pca_df["PC2"][i]))
        ax.set_xlabel("Principal Component 1")
        ax.set_ylabel("Principal Component 2")
        ax.set_title("PCA Analysis of Hitting Trends")
        st.pyplot(fig)

        st.write(f"**Explained Variance:** PC1: {variance[0]*100:.2f}%, PC2: {variance[1]*100:.2f}%")

        # PCA Feature Contributions
        loadings_df = pd.DataFrame(loadings, columns=feature_names, index=["PC1", "PC2"])
        fig, ax = plt.subplots(figsize=(10, 6))
        loadings_df.T.plot(kind="bar", ax=ax)
        ax.set_title("PCA Feature Contributions to PC1 and PC2")
        ax.set_ylabel("Contribution Magnitude")
        ax.set_xlabel("Hitting Metrics")
        ax.legend(title="Principal Components")
        st.pyplot(fig)

        st.dataframe(loadings_df.T.style.format("{:.2f}"))

    else:
        st.warning("⚠️ Not enough valid data for PCA analysis.")

    # Interpretation of Data
    st.title("Interpretation of Data: ")
    st.write("1950 is far from modern eras, suggesting hitting styles were very different back then. \n"
             "\n1960-1970 are close together, implying minimal changes in that period.\n\n1980 starts shifting,"
             " possibly reflecting an increase in power hitting.\n\n2000 is farthest apart, which may be due to "
             "the steroid era, where power numbers surged.\n\n2010 moves back toward 1990, "
             "indicating a post-steroid era adjustment in hitting trends.")

    st.write("### **Principal Component Analysis (PCA) Findings:**")
    st.markdown("### **Interpreting Principal Components (PC1 & PC2)**")

    st.write("- **PC1 represents the shift from contact hitting to power-hitting.**")
    st.write("  - Higher PC1 values indicate more **home runs and strikeouts** (modern power approach).")
    st.write(
        "  - Lower PC1 values reflect **high batting averages, more walks, and fewer strikeouts** (traditional contact hitting).")

    st.write("- **PC2 differentiates between sluggers and plate-discipline hitters.**")
    st.write("  - Higher PC2 values align with **power hitters who excel at slugging and extra-base hits**.")
    st.write(
        "  - Lower PC2 values are linked to **players with strong plate discipline, prioritizing walks and on-base percentage over raw power.**")

    st.write(
        "- **A high PC1 score suggests a power-heavy decade, emphasizing home runs at the cost of contact and walks.**")
    st.write(
        "  - This trend aligns with **modern baseball**, where hitters accept high strikeout rates in exchange for greater power output.")

    st.write(
        "- **A high PC2 score indicates a preference for aggressive, high-slugging hitters over those who prioritize patience and walks.**")
    st.write(
        "  - Lower PC2 values suggest a more balanced or disciplined offensive approach, with an emphasis on **on-base skills over raw power.**")

    st.write("### **Conclusion:**")
    st.write("- The biggest jump appears from **1980 to 2000**, which aligns with the home run surge and changing offensive philosophies.")
    st.write("- **1950 was an outlier**, suggesting a fundamentally different offensive approach compared to later years.")
    st.write("- **1960 and 1970 demonstrate a close relationship**, showing that hitting remained relatively stable.")
    st.write("- **Modern decades (1990-2010) cluster closer together**, suggesting hitting strategies have stabilized after the steroid era.")

    st.markdown(":red[Continue to Hitting Trends Analysis to Continue the investigation]")
