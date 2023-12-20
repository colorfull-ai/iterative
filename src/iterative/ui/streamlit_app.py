# Main Streamlit Interface
import streamlit as st
from iterative.service.utils.project_utils import get_project_root
from iterative.service.utils.streamlit_utils import find_streamlit_scripts
from iterative.ui.gpt_chat import main as gpt_chat_main
from iterative.ui.assistant_chat import main as assistant_chat_main


# Get the project root directory
project_root = get_project_root()

app_mode = st.sidebar.selectbox('Choose the app mode', ['Home', 'ChatGPT Clone', 'Assistant', 'Other Sections'])

if app_mode == 'ChatGPT Clone':
    gpt_chat_main()

elif app_mode == 'Assistant':
    assistant_chat_main()
elif app_mode == 'Home':
    # Dynamically import Streamlit sections
    streamlit_scripts = find_streamlit_scripts(project_root)

    # Define a routing dictionary
    sections = streamlit_scripts

    # Sidebar for navigation
    selected_section = st.sidebar.selectbox("Choose a section", list(sections.keys()))

    # Display the chosen section
    if selected_section in sections:
        sections[selected_section]()
