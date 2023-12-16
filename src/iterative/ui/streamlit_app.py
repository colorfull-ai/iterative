# Main Streamlit Interface
import streamlit as st
from iterative.service.utils.project_utils import get_project_root
from iterative.service.utils.streamlit_utils import find_streamlit_scripts

st.title('Iterative Project Tools')

# Get the project root directory
project_root = get_project_root()

# Dynamically import Streamlit sections
streamlit_scripts = find_streamlit_scripts(project_root)

# Define a routing dictionary
sections = streamlit_scripts

# Sidebar for navigation
selected_section = st.sidebar.selectbox("Choose a section", list(sections.keys()))

# Display the chosen section
if selected_section in sections:
    sections[selected_section]()
