import streamlit as st

# Page title
def show():
    st.title("My Thesis on Baseball Stats & Machine Learning")

# Brief description
    st.write(
      "In this video the different TSNEs of hitters is displayed, the general idea of this section is to display"
      "just how different the decades are from each other, some share similarities while others do not resemble"
      "the other in the slightest "
    )

    # Embed YouTube video
    st.video("https://youtu.be/QTlPt20pQaU")