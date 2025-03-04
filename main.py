import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from baseball_pages import dashboard, thesis_overview, video, insights

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to",
                        ["Dashboard", "Thesis Overview", "YouTube Video", "Insights", "Hitting Trends Analysis"])

if page == "Dashboard":
    dashboard.show()
elif page == "Thesis Overview":
    thesis_overview.show()
elif page == "YouTube Video":
    video.show()
elif page == "Insights":
    insights.show()
elif page == "Hitting Trends Analysis":
    st.title("Hitting Trends Analysis (1950-2010)")


    # Load datasets
    @st.cache_data
    def load_data():
        decades = ["1950", "1960", "1970", "1980", "1990", "2000", "2010"]
        base_path = "C:/Users/j.mcintosh25/Documents/BaseballThesis/"
        files = [f"{base_path}{decade}stats.csv" for decade in decades]
        data = {}
        for decade, file in zip(decades, files):
            try:
                df = pd.read_csv(file, encoding='ISO-8859-1')
                df.columns = df.columns.str.replace("ï»¿", "").str.strip()  # Clean column names
                data[decade] = df
            except Exception as e:
                st.warning(f"Error loading {file}: {e}")
                data[decade] = pd.DataFrame()
        return data


    data = load_data()


    # Process data
    def process_data(data):
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


    summary_stats_avg, avg_HR, avg_K, avg_BB = process_data(data)

    # Sidebar plot selection
    plot_option = st.sidebar.selectbox(
        "Select a plot:",
        ["Hitting Trends - Averages", "Average HRs per Player", "Average Strikeouts per Player",
         "Average Walks per Player"]
    )


    # Plot function
    def plot_trends(summary_stats, title):
        if summary_stats.empty:
            st.warning("No valid data to plot.")
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


    # Plot per-player averages
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


    # Display selected plot
    if plot_option == "Hitting Trends - Averages":
        plot_trends(summary_stats_avg, "Hitting Trends - Averages (1950-2010)")
    elif plot_option == "Average HRs per Player":
        plot_avg_totals(avg_HR, "Average Home Runs Per Player Per Decade", "Avg HRs per Player")
    elif plot_option == "Average Strikeouts per Player":
        plot_avg_totals(avg_K, "Average Strikeouts Per Player Per Decade", "Avg Strikeouts per Player")
    elif plot_option == "Average Walks per Player":
        plot_avg_totals(avg_BB, "Average Walks Per Player Per Decade", "Avg Walks per Player")
