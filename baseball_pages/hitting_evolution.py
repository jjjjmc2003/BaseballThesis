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

        # Flip PC1 to represent increasing Contact Hitting
        pca_results[:, 0] = -pca_results[:, 0]  # Flip PC1 scores
        loadings[0, :] = -loadings[0, :]  # Flip PC1 loadings

        pca_df = pd.DataFrame(pca_results, columns=["PC1", "PC2"], index=summary_stats_avg.columns)

        # PCA Scatter Plot
        fig, ax = plt.subplots()
        ax.scatter(pca_df["PC1"], pca_df["PC2"], color="blue")
        for i, txt in enumerate(pca_df.index):
            ax.annotate(txt, (pca_df["PC1"][i], pca_df["PC2"][i]))
        ax.set_xlabel("Principal Component 1 (Contact Component)")
        ax.set_ylabel("Principal Component 2 (Power Component)")
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

    st.write(
        "1950 appears isolated from the modern eras, indicating a significantly different offensive profile. "
        "Its position suggests low contact and low power metrics, likely reflective of a more balanced or conservative hitting era.\n\n"
        "1960 and 1970 are clustered together, indicating stability in offensive strategies, with a slight increase in contact metrics.\n\n"
        "By 1980, we begin to see a noticeable shift toward higher power metrics and lower contact efficiency, "
        "marking the early transition to modern hitting approaches.\n\n"
        "2000 stands out the most, moving farthest left along PC1 and highest along PC2, consistent with the steroid era's focus on extreme power "
        "— high home run rates, strikeouts, and slugging.\n\n"
        "2010 shifts back toward the center, closer to 1990, suggesting a partial recalibration away from peak power, "
        "possibly due to improved testing and a renewed emphasis on balanced hitting."
    )

    st.write("### **Principal Component Analysis (PCA) Findings:**")
    st.markdown("### **Interpreting Principal Components (PC1 & PC2)**")

    st.write("- **PC1 represents the axis from power hitting to contact hitting.**")
    st.write(
        "  - **Higher PC1 values** reflect **high batting averages, more walks, and fewer strikeouts** (traditional contact hitters).")
    st.write(
        "  - **Lower PC1 values** indicate **more home runs, higher strikeout rates, and lower walk/contact skills** (modern power hitters).")

    st.write("- **PC2 still differentiates between sluggers and disciplined hitters.**")
    st.write("  - **Higher PC2 values** align with **aggressive sluggers focused on extra-base hits and high SLG**.")
    st.write("  - **Lower PC2 values** suggest **plate-discipline hitters**, who emphasize OBP and BB% over raw power.")

    st.write(
        "- **A low PC1 score now signifies a power-heavy decade**, where home runs and strikeouts dominate, often at the cost of consistent contact or plate discipline.")
    st.write(
        "- **A high PC1 score reflects a contact-driven era**, prioritizing getting on base, minimizing strikeouts, and hitting for average.")

    st.write(
        "- **A high PC2 score represents slug-first hitters**, while lower PC2 scores indicate more balanced or OBP-focused profiles.")

    st.write("### **Conclusion:**")
    st.write(
        "- The **most dramatic shift** occurs from **1980 to 2000**, aligning with the steroid era and power surge in MLB.")
    st.write(
        "- **1950** is a clear outlier with low contact and low power, suggesting a more conservative offensive environment.")
    st.write("- **1960–1970** show continuity, with modest increases in contact metrics.")
    st.write(
        "- **1990 to 2010** form a relatively tight cluster, implying that modern hitting philosophies had stabilized post-2000.")

    st.markdown(":red[Continue to Hitting Trends Analysis to Continue the investigation]")

