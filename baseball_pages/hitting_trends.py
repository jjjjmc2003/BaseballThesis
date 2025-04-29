import pandas as pd # Import pandas for data processing
import matplotlib.pyplot as plt # Import matplotlib for plotting
import seaborn as sns # Import seaborn for advanced plotting
import streamlit as st # Import streamlit for creating a web app
import os # Import os for file handling

# Streamlit App Title
st.title("Hitting Trends Analysis (1950-2010)") # Set the title of the Streamlit app

# Load datasets
@st.cache_data # Cache the function to optimize performance
def load_data():
    # Define the decades to analyze
    decades = ["1950", "1960", "1970", "1980", "1990", "2000", "2010"]
    # Define the base path for the data files
    base_path = "C:/Users/j.mcintosh25/Documents/BaseballThesis/"
    # Create file paths for each decade
    files = [f"{base_path}{decade}stats.csv" for decade in decades]
    data = {} # Initialize an empty dictionary to store data
    for decade, file in zip(decades, files): # Loop through decades and their corresponding files
        try:
            # Read the CSV file for the current decade
            df = pd.read_csv(file, encoding='ISO-8859-1')
            # Clean column names by removing unwanted characters and whitespace
            df.columns = df.columns.str.replace("ï»¿", "").str.strip()
            data[decade] = df # Store the DataFrame in the dictionary
        except Exception as e: # Handle exceptions during file loading
            # Display a warning message in the Streamlit app
            st.warning(f"Error loading {file}: {e}")
            data[decade] = pd.DataFrame() # Store an empty DataFrame in case of error
    return data # Return the loaded data

data = load_data() # Load the data using the load_data function

# Process data to compute averages per player
def process_data(data):
    # Define the key statistics to extract
    key_stats = ["BA", "OBP", "SLG", "HR", "SO", "BB", "PA"]
    processed_avg = {} # Initialize a dictionary to store processed averages
    avg_HR = {} # Initialize a dictionary to store average home runs
    avg_K = {} # Initialize a dictionary to store average strikeouts
    avg_BB = {} # Initialize a dictionary to store average walks

    for decade, df in data.items(): # Loop through each decade and its data
        df.columns = df.columns.str.strip() # Clean column names
        # Check for missing columns in the current DataFrame
        missing_cols = [col for col in key_stats if col not in df.columns]
        if missing_cols: # If there are missing columns
            # Display a warning message in the Streamlit app
            st.warning(f"Warning: Missing columns in {decade}: {missing_cols}")
            continue # Skip processing for this decade

        df = df[key_stats].copy() # Create a copy of the DataFrame with only key stats
        df.rename(columns={"SO": "K"}, inplace=True) # Rename "SO" to "K" for consistency

        # Calculate additional metrics
        df["HR/PA"] = df["HR"] / df["PA"] # Calculate home runs per plate appearance
        df["K%"] = df["K"] / df["PA"] # Calculate strikeout percentage
        df["BB%"] = df["BB"] / df["PA"] # Calculate walk percentage
        processed_avg[decade] = df.mean() # Calculate and store the mean of each column

        avg_HR[decade] = df["HR"].mean() # Calculate and store the average home runs
        avg_K[decade] = df["K"].mean() # Calculate and store the average strikeouts
        avg_BB[decade] = df["BB"].mean() # Calculate and store the average walks

    # Return the processed averages and individual metrics
    return pd.DataFrame(processed_avg), pd.Series(avg_HR, name="Avg HR per Player"), pd.Series(avg_K,
                                                                                               name="Avg K per Player"), pd.Series(
        avg_BB, name="Avg BB per Player")

# Process the data and calculate summary statistics
summary_stats_avg, avg_HR, avg_K, avg_BB = process_data(data)

# Plot Function for Streamlit
def plot_trends(summary_stats, title):
    if summary_stats.empty: # Check if the summary statistics are empty
        st.warning("No valid data to plot.") # Display a warning if no data is available
        return # Exit the function

    summary_stats = summary_stats.T # Transpose the DataFrame for plotting
    summary_stats.index = summary_stats.index.astype(int) # Convert the index to integers

    fig, ax = plt.subplots(figsize=(10, 5)) # Create a matplotlib figure and axis
    for col in ["BA", "OBP", "SLG", "HR/PA", "K%", "BB%"]: # Loop through the columns to plot
        if col in summary_stats.columns: # Check if the column exists in the DataFrame
            ax.plot(summary_stats.index, summary_stats[col], marker='o', label=col) # Plot the column

    ax.set_xlabel("Decade") # Set the x-axis label
    ax.set_ylabel("Metric Value") # Set the y-axis label
    ax.set_title(title) # Set the plot title
    ax.legend() # Add a legend to the plot
    ax.grid() # Add a grid to the plot

    st.pyplot(fig) # Display the plot in the Streamlit app

# Plot average HRs, strikeouts, and walks per player
def plot_avg_totals(avg_series, title, ylabel):
    fig, ax = plt.subplots(figsize=(10, 5)) # Create a matplotlib figure and axis
    avg_series.index = avg_series.index.astype(int) # Convert the index to integers
    ax.plot(avg_series.index, avg_series.values, marker='o', linestyle='-', label=title) # Plot the series

    ax.set_xlabel("Decade") # Set the x-axis label
    ax.set_ylabel(ylabel) # Set the y-axis label
    ax.set_title(title) # Set the plot title
    ax.legend() # Add a legend to the plot
    ax.grid() # Add a grid to the plot

    st.pyplot(fig) # Display the plot in the Streamlit app

# Streamlit Sidebar for Plot Selection
plot_option = st.sidebar.selectbox( # Create a dropdown menu in the sidebar
    "Select a plot:", # Label for the dropdown menu
    ["Hitting Trends - Averages", "Average HRs per Player", "Average Strikeouts per Player", "Average Walks per Player"] # Options
)

# Display selected plot
if plot_option == "Hitting Trends - Averages": # Check if the user selected "Hitting Trends - Averages"
    plot_trends(summary_stats_avg, "Hitting Trends - Averages (1950-2010)") # Plot hitting trends
elif plot_option == "Average HRs per Player": # Check if the user selected "Average HRs per Player"
    plot_avg_totals(avg_HR, "Average Home Runs Per Player Per Decade", "Avg HRs per Player") # Plot average home runs
elif plot_option == "Average Strikeouts per Player": # Check if the user selected "Average Strikeouts per Player"
    plot_avg_totals(avg_K, "Average Strikeouts Per Player Per Decade", "Avg Strikeouts per Player") # Plot average strikeouts
elif plot_option == "Average Walks per Player": # Check if the user selected "Average Walks per Player"
    plot_avg_totals(avg_BB, "Average Walks Per Player Per Decade", "Avg Walks per Player") # Plot average walks