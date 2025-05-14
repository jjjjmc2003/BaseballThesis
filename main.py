# Import necessary libraries
import streamlit as st  # Streamlit for creating the web app
import pandas as pd  # Pandas for data manipulation
import os  # OS module for file and directory operations
import requests  # Requests library for handling HTTP requests
import matplotlib.pyplot as plt  # Matplotlib for creating visualizations
import datetime  # Datetime module for handling date and time
from baseball_pages import dashboard, video, hitting_evolution, players, chatbot, yearly_analysis  # Import custom modules

# Set up the Streamlit sidebar for navigation
st.sidebar.title("Navigation")  # Title for the sidebar
page = st.sidebar.radio("Go to", [  # Radio button for page selection
    "Dashboard",  # Option for the Dashboard page
    "Year by Year TSNE",  # Option for Year-by-Year TSNE visualizations
    "Players (Contact vs Power)",  # Option for player comparison page
    "Analysis of Hitting Evolution",  # Option for hitting evolution analysis
    "Decade Hitting Trends Analysis",  # Option for decade-level trend analysis
    "Year by Year Hitting Analysis",  # Option for yearly hitting analysis
    "Chatbot",  # Option for the chatbot page
])

# Route to the appropriate page based on user selection
if page == "Dashboard":
    dashboard.show()  # Display the Dashboard page

    requests.post("https://hooks.zapier.com/hooks/catch/22833993/2nj036y/",
                  data={"event": "View", "page viewed": "Dashboard",
                        "timestamp": datetime.datetime.utcnow().isoformat()})  # Log the event
    requests.post("https://john-mcintosh-practice.app.n8n.cloud/webhook/387e4a84-07b9-402d-816d-3bae9d689d06",
                  data={"event": "View", "page viewed": "Dashboard",
                            "timestamp": datetime.datetime.utcnow().isoformat()})  # Log the event


elif page == "Year by Year TSNE":
    video.show()  # Display the Year by Year TSNE visualizations

    requests.post("https://hooks.zapier.com/hooks/catch/22833993/2nj036y/",
                      data={"event": "view", "page viewed": "Year-by-Year TSNE",
                            "timestamp": datetime.datetime.utcnow().isoformat()})
    requests.post("https://john-mcintosh-practice.app.n8n.cloud/webhook/387e4a84-07b9-402d-816d-3bae9d689d06",
                      data={"event": "View", "page viewed": "Year by Year TSNE",
                            "timestamp": datetime.datetime.utcnow().isoformat()})




elif page == "Players (Contact vs Power)":
    players.show()  # Display the player comparison page


    requests.post("https://hooks.zapier.com/hooks/catch/22833993/2nj036y/",
                      data={"event": "view", "page viewed": "Players (Contact vs Power)",
                            "timestamp": datetime.datetime.utcnow().isoformat()})
    requests.post("https://john-mcintosh-practice.app.n8n.cloud/webhook/387e4a84-07b9-402d-816d-3bae9d689d06",
                      data={"event": "View", "page viewed": "Players (Contact vs Power)",
                            "timestamp": datetime.datetime.utcnow().isoformat()})



elif page == "Analysis of Hitting Evolution":
    hitting_evolution.show()  # Display the hitting evolution analysis page

    requests.post("https://hooks.zapier.com/hooks/catch/22833993/2nj036y/",
                      data={"event": "view", "page viewed": "Analysis of Hitting Evolution",
                            "timestamp": datetime.datetime.utcnow().isoformat()})
    requests.post("https://john-mcintosh-practice.app.n8n.cloud/webhook/387e4a84-07b9-402d-816d-3bae9d689d06",
                      data={"event": "View", "page viewed": "Analysis of Hitting Evolution",
                            "timestamp": datetime.datetime.utcnow().isoformat()})



elif page == "Decade Hitting Trends Analysis":
    # Title for the Decade Hitting Trends Analysis page
    st.title("Decade Hitting Trends Analysis")

    requests.post("https://hooks.zapier.com/hooks/catch/22833993/2nj036y/", data={"event": "view", "page viewed": "Decade Hitting Trends Analysis",  "timestamp": datetime.datetime.utcnow().isoformat()})
    requests.post("https://john-mcintosh-practice.app.n8n.cloud/webhook/387e4a84-07b9-402d-816d-3bae9d689d06",
                      data={"event": "View", "page viewed": "Decade Hitting Trends Analysis",
                            "timestamp": datetime.datetime.utcnow().isoformat()})

    # Set up the local data directory
    DATA_DIR = "data"  # Directory to store data files
    os.makedirs(DATA_DIR, exist_ok=True)  # Create the directory if it doesn't exist

    # Define the GitHub repository URL for data files
    GITHUB_REPO = "https://raw.githubusercontent.com/jjjjmc2003/BaseballThesis/main/data/"
    decades = ["1950", "1960", "1970", "1980", "1990", "2000", "2010"]  # List of decades
    files = [f"{decade}stats.csv" for decade in decades]  # Generate file names for each decade

    # Function to download missing files from the GitHub repository
    def download_file(file_name):
        url = f"{GITHUB_REPO}{file_name}"  # Construct the file URL
        local_path = os.path.join(DATA_DIR, file_name)  # Local file path

        if not os.path.exists(local_path):  # Check if the file already exists locally
            try:
                response = requests.get(url, stream=True)  # Send an HTTP GET request
                if response.status_code == 200:  # Check if the request was successful
                    with open(local_path, "wb") as f:  # Open the file in write-binary mode
                        f.write(response.content)  # Write the content to the file
                    st.success(f"Downloaded: {file_name}")  # Show a success message
                else:
                    st.error(f"❌ Error downloading {file_name} (HTTP {response.status_code})")  # Show an error message
            except Exception as e:  # Handle exceptions
                st.error(f"❌ Failed to download {file_name}: {e}")  # Show an error message

    # Download all missing files
    for file in files:
        download_file(file)  # Call the download function for each file

    # Function to load data from local files
    @st.cache_data  # Cache the function to optimize performance
    def load_data():
        data = {}  # Dictionary to store data for each decade
        for file in files:
            file_path = os.path.join(DATA_DIR, file)  # Construct the file path
            try:
                df = pd.read_csv(file_path, encoding="ISO-8859-1")  # Read the CSV file into a DataFrame
                df.columns = df.columns.str.strip()  # Strip whitespace from column names
                data[file.split("stats")[0]] = df  # Use the decade as the key
            except Exception as e:  # Handle exceptions
                st.error(f"❌ Error loading {file}: {e}")  # Show an error message
        return data  # Return the loaded data

    data = load_data()  # Load the data using the load_data function

    # Show a confirmation message if data is successfully loaded
    if data:
        st.write("Successfully loaded all available data!")

    # Radio button for dataset selection
    player_type = st.radio("Choose dataset:", ["All Players", "Starters Only (PA ≥ 100)"])  # Dataset options

    # Function to process data based on the selected dataset
    def process_data(data, player_type):
        key_stats = ["BA", "OBP", "SLG", "HR", "SO", "BB", "PA"]  # Key statistics to analyze
        processed_avg = {}  # Dictionary to store processed averages
        avg_HR = {}  # Dictionary to store average home runs
        avg_K = {}  # Dictionary to store average strikeouts
        avg_BB = {}  # Dictionary to store average walks

        for decade, df in data.items():  # Loop through each decade and its data
            df.columns = df.columns.str.strip()  # Strip whitespace from column names
            missing_cols = [col for col in key_stats if col not in df.columns]  # Check for missing columns
            if missing_cols:  # If there are missing columns
                st.warning(f"Warning: Missing columns in {decade}: {missing_cols}")  # Show a warning message
                continue  # Skip processing for this decade

            df = df[key_stats].copy()  # Create a copy of the DataFrame with only key stats
            if player_type == "Starters Only (PA ≥ 100)":  # Filter for starters if selected
                df = df[df["PA"] >= 100]

            df.rename(columns={"SO": "K"}, inplace=True)  # Rename "SO" to "K" for consistency

            # Calculate additional metrics
            df["HR/PA"] = df["HR"] / df["PA"]  # Home runs per plate appearance
            df["K%"] = df["K"] / df["PA"]  # Strikeout percentage
            df["BB%"] = df["BB"] / df["PA"]  # Walk percentage
            processed_avg[decade] = df.mean()  # Calculate and store the mean of each column

            avg_HR[decade] = df["HR"].mean()  # Average home runs
            avg_K[decade] = df["K"].mean()  # Average strikeouts
            avg_BB[decade] = df["BB"].mean()  # Average walks

        return pd.DataFrame(processed_avg), pd.Series(avg_HR, name="Avg HR per Player"), pd.Series(avg_K,
                                                                                                   name="Avg K per Player"), pd.Series(
            avg_BB, name="Avg BB per Player")  # Return processed data

    # Process the data based on the selected dataset
    summary_stats_avg, avg_HR, avg_K, avg_BB = process_data(data, player_type)

    # Sidebar dropdown for plot selection
    plot_option = st.sidebar.selectbox(
        "Select a plot:",  # Label for the dropdown
        ["Hitting Trends - Averages", "Average HRs per Player", "Average Strikeouts per Player",
         "Average Walks per Player"]  # Plot options
    )

    # Function to plot trends for hitting metrics
    def plot_trends(summary_stats, title):
        if summary_stats.empty:  # Check if the summary statistics are empty
            st.warning("No valid data to plot.")  # Show a warning if no data is available
            return  # Exit the function

        summary_stats = summary_stats.T  # Transpose the DataFrame for plotting
        summary_stats.index = summary_stats.index.astype(int)  # Convert the index to integers

        fig, ax = plt.subplots(figsize=(10, 5))  # Create a matplotlib figure and axis
        for col in ["BA", "OBP", "SLG", "HR/PA", "K%", "BB%"]:  # Loop through the columns to plot
            if col in summary_stats.columns:  # Check if the column exists in the DataFrame
                ax.plot(summary_stats.index, summary_stats[col], marker='o', label=col)  # Plot the column

        ax.set_xlabel("Decade")  # Set the x-axis label
        ax.set_ylabel("Metric Value")  # Set the y-axis label
        ax.set_title(title)  # Set the plot title
        ax.legend()  # Add a legend to the plot
        ax.grid()  # Add a grid to the plot

        st.pyplot(fig)  # Display the plot in the Streamlit app

    # Function to plot averages for individual metrics
    def plot_avg_totals(avg_series, title, ylabel):
        fig, ax = plt.subplots(figsize=(10, 5))  # Create a matplotlib figure and axis
        avg_series.index = avg_series.index.astype(int)  # Convert the index to integers
        ax.plot(avg_series.index, avg_series.values, marker='o', linestyle='-', label=title)  # Plot the series

        ax.set_xlabel("Decade")  # Set the x-axis label
        ax.set_ylabel(ylabel)  # Set the y-axis label
        ax.set_title(title)  # Set the plot title
        ax.legend()  # Add a legend to the plot
        ax.grid()  # Add a grid to the plot

        st.pyplot(fig)  # Display the plot in the Streamlit app

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
    chatbot.show()  # Display the chatbot page

    requests.post("https://hooks.zapier.com/hooks/catch/22833993/2nj036y/", data={"event": "view", "page viewed": "Chatbot",  "timestamp": datetime.datetime.utcnow().isoformat()})
    requests.post("https://john-mcintosh-practice.app.n8n.cloud/webhook/387e4a84-07b9-402d-816d-3bae9d689d06",
                      data={"event": "View", "page viewed": "Chatbot",
                            "timestamp": datetime.datetime.utcnow().isoformat()})


elif page == "Year by Year Hitting Analysis":
    yearly_analysis.show()  # Display the yearly hitting analysis page

    requests.post("https://hooks.zapier.com/hooks/catch/22833993/2nj036y/", data={"event": "view", "page viewed": "Year by Year Hitting Analysis",  "timestamp": datetime.datetime.utcnow().isoformat()})
    requests.post("https://john-mcintosh-practice.app.n8n.cloud/webhook/387e4a84-07b9-402d-816d-3bae9d689d06",
                      data={"event": "View", "page viewed": "Year by Year Hitting Analysis",
                            "timestamp": datetime.datetime.utcnow().isoformat()})

