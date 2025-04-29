# Import necessary libraries
import streamlit as st  # Streamlit for creating the web app
import pandas as pd  # Pandas for data manipulation
import plotly.express as px  # Plotly for creating interactive visualizations

# Define the main function to display the page
def show():
    # Set the title of the page
    st.title("📈 Year-by-Year Hitting Analysis (1950–2010)")
    # Add a caption to provide context about the page
    st.caption("Explore MLB hitting stats trends for each individual year")
    # Add a note about MLB player strikes in specific years
    st.caption("Note: There were player strikes in the MLB in the years 1981 and 1994 that caused fewer games to be played")

    # Create a radio button for the user to select the dataset
    data_choice = st.radio(
        "Choose dataset:",  # Label for the radio button
        ["All Players", "Starters Only (PA ≥ 100)"]  # Options for the user to choose from
    )

    # Set the file path based on the user's choice
    if data_choice == "All Players":
        data_path = "data/combined_yearly_stats_all_players.csv"  # Path for all players dataset
    else:
        data_path = "data/combined_yearly_stats_starters_only.csv"  # Path for starters-only dataset

    # Try to load the selected dataset
    try:
        df = pd.read_csv(data_path)  # Read the CSV file into a DataFrame
    except FileNotFoundError:  # Handle the case where the file is not found
        st.error("🚫 Data file not found. Please check your file paths or run the combiner script.")  # Show an error message
        return  # Exit the function if the file is not found

    # Create a dropdown menu for the user to select a metric to visualize
    metric = st.selectbox(
        "Select a metric to visualize:",  # Label for the dropdown
        options=["HR", "SO", "BB", "BA", "OBP", "SLG", "K%", "BB%", "HR/PA"]  # List of metrics to choose from
    )

    # Group the data by year and calculate the average of the selected metric
    agg_df = df.groupby("Year")[metric].mean().reset_index()  # Group by year and calculate the mean
    agg_df["Year"] = agg_df["Year"].astype(int)  # Convert the year column to integers
    agg_df["Year"] = agg_df["Year"].apply(lambda x: str(x))  # Convert the year column to strings

    # Create a line plot using Plotly
    fig = px.line(
        agg_df,  # Data for the plot
        x="Year",  # X-axis: Year
        y=metric,  # Y-axis: Selected metric
        title=f"Average {metric} by Year ({data_choice})",  # Title of the plot
        markers=True  # Add markers to the line plot
    )
    st.plotly_chart(fig, use_container_width=True)  # Display the plot in the Streamlit app

    # Display the data table of average values by year
    st.write("Average Values by Year of Selected Metric:")  # Add a label for the table
    st.dataframe(agg_df)  # Show the DataFrame as a table