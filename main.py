import streamlit as st
import pandas as pd
import os
import requests
import matplotlib.pyplot as plt
from baseball_pages import dashboard, thesis_overview, video, hitting_evolution, players, chatbot, yearly_analysis

# Streamlit Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Dashboard",
    "Year by Year TSNE",
    "Players (Contact vs Power)",
    "Analysis of Hitting Evolution",
    "Decade Hitting Trends Analysis",
    "Year by Year Hitting Trend Analysis",
    "Chatbot",

])

# If Dashboard selected
if page == "Dashboard":
    dashboard.show()

# If TSNE selected
elif page == "Year by Year TSNE":
    video.show()

elif page == "Players (Contact vs Power)":
    players.show();

elif page == "Analysis of Hitting Evolution":
    hitting_evolution.show()
# If Hitting Trends Analysis selected
elif page == "Decade Hitting Trends Analysis":
    # Streamlit Title
    st.title("Decade Hitting Trends Analysis")

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
                    st.success(f" Downloaded: {file_name}")
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
        st.write("Successfully loaded all available data!")

    # ⬅️ Add this near the top of the file after loading data
    player_type = st.radio("Choose dataset:", ["All Players", "Starters Only (PA ≥ 100)"])


    # ✅ Modified function with player_type input
    def process_data(data, player_type):
        key_stats = ["BA", "OBP", "SLG", "HR", "SO", "BB", "PA"]
        processed_avg = {}
        avg_HR = {}
        avg_K = {}
        avg_BB = {}

        for decade, df in data.items():
            df.columns = df.columns.str.strip()
            missing_cols = [col for col in key_stats if col not in df.columns]
            if missing_cols:
                st.warning(f"Warning: Missing columns in {decade}: {missing_cols}")
                continue

            df = df[key_stats].copy()
            if player_type == "Starters Only (PA ≥ 100)":
                df = df[df["PA"] >= 100]

            df.rename(columns={"SO": "K"}, inplace=True)

            df["HR/PA"] = df["HR"] / df["PA"]
            df["K%"] = df["K"] / df["PA"]
            df["BB%"] = df["BB"] / df["PA"]
            processed_avg[decade] = df.mean()

            avg_HR[decade] = df["HR"].mean()
            avg_K[decade] = df["K"].mean()
            avg_BB[decade] = df["BB"].mean()

        return pd.DataFrame(processed_avg), pd.Series(avg_HR, name="Avg HR per Player"), pd.Series(avg_K,
                                                                                                   name="Avg K per Player"), pd.Series(
            avg_BB, name="Avg BB per Player")


    # 🔁 Recompute based on selection
    summary_stats_avg, avg_HR, avg_K, avg_BB = process_data(data, player_type)

    # Sidebar Navigation for Plot Selection
    plot_option = st.sidebar.selectbox(
        "Select a plot:",
        ["Hitting Trends - Averages", "Average HRs per Player", "Average Strikeouts per Player",
         "Average Walks per Player"]
    )

    # Function to Plot Trends
    def plot_trends(summary_stats, title):
        if summary_stats.empty:
            st.warning(" No valid data to plot.")
            return

        summary_stats = summary_stats.T
        summary_stats.index = summary_stats.index.astype(int)

        fig, ax = plt.subplots(figsize=(10, 5))
        for col in ["BA", "OBP", "SLG", "HR/PA", "K%", "BB%"]:
            if col in summary_stats.columns:
                ax.plot(summary_stats.index, summary_stats[col], marker='o', label=col)

        ax.set_xlabel("Decade")
        ax.set_ylabel("Metric Value")
        ax.set_title(title)
        ax.legend()
        ax.grid()

        st.pyplot(fig)

    # Function to Plot Per-Player Averages
    def plot_avg_totals(avg_series, title, ylabel):
        fig, ax = plt.subplots(figsize=(10, 5))
        avg_series.index = avg_series.index.astype(int)
        ax.plot(avg_series.index, avg_series.values, marker='o', linestyle='-', label=title)

        ax.set_xlabel("Decade")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend()
        ax.grid()

        st.pyplot(fig)

    # Display the selected plot
    if plot_option == "Hitting Trends - Averages":
        plot_trends(summary_stats_avg, "Hitting Trends - Averages (1950-2010)")
    elif plot_option == "Average HRs per Player":
        plot_avg_totals(avg_HR, "Average Home Runs Per Player Per Decade", "Avg HRs per Player")
    elif plot_option == "Average Strikeouts per Player":
        plot_avg_totals(avg_K, "Average Strikeouts Per Player Per Decade", "Avg Strikeouts per Player")
    elif plot_option == "Average Walks per Player":
        plot_avg_totals(avg_BB, "Average Walks Per Player Per Decade", "Avg Walks per Player")

elif page == "Chatbot":
    chatbot.show()

elif page == "Year by Year Hitting Trend Analysis":
    yearly_analysis.show()

