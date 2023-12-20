# Main Streamlit Interface
import streamlit as st
from iterative.service.utils.project_utils import get_project_root
from iterative.service.utils.streamlit_utils import find_streamlit_scripts
from iterative.ui.gpt_chat import main as gpt_chat_main
from iterative.ui.assistant_chat import main as assistant_chat_main

current_project_root_dir = get_project_root()
current_project_name = current_project_root_dir.split('/')[-1]

app_mode = st.sidebar.selectbox('Choose the app mode', ['Home', 'ChatGPT Clone', 'Assistant', f'PROJECT: {current_project_name}'])

if app_mode == 'ChatGPT Clone':
    gpt_chat_main()

elif app_mode == 'Assistant':
    assistant_chat_main()
elif app_mode == 'Home':
    streamlit_scripts = find_streamlit_scripts()

    if not streamlit_scripts:
        st.write("No sections found.")
    else:
        # Define a routing dictionary
        sections = streamlit_scripts

        # Sidebar for navigation
        selected_section = st.sidebar.selectbox("Choose a section", list(sections.keys()))

        # Display the chosen section
        if selected_section in sections:
            sections[selected_section]()