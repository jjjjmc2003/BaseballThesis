import streamlit as st
import pandas as pd
import plotly.express as px

def show():
    st.title("📈 Year-by-Year Hitting Analysis (1950–2010)")
    st.caption("Explore MLB hitting stats trends for each individual year")
    st.caption("Note: There were player strikes in the MLB in the years 1981 and 1994 that caused fewer games to be played")

    # Data source selector
    data_choice = st.radio(
        "Choose dataset:",
        ["All Players", "Starters Only (PA ≥ 100)"]
    )

    if data_choice == "All Players":
        data_path = "data/combined_yearly_stats_all_players.csv"
    else:
        data_path = "data/combined_yearly_stats_starters_only.csv"

    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        st.error("🚫 Data file not found. Please check your file paths or run the combiner script.")
        return

    metric = st.selectbox("Select a metric to visualize:", options=["HR", "SO", "BB", "BA", "OBP", "SLG", "K%", "BB%", "HR/PA"])

    # Calculate average by year
    agg_df = df.groupby("Year")[metric].mean().reset_index()
    agg_df["Year"] = agg_df["Year"].astype(int)  # Ensure it's int
    agg_df["Year"] = agg_df["Year"].apply(lambda x: str(x))  # Force string, removes comma

    # Plot with Plotly
    fig = px.line(
        agg_df,
        x="Year",
        y=metric,
        title=f"Average {metric} by Year ({data_choice})",
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

    # Show data table
    st.write("Average Values by Year of Selected Metric:")
    st.dataframe(agg_df)
