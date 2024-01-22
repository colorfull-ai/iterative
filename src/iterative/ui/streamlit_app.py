# Main Streamlit Interface
import streamlit as st
from iterative.service.project_management.service.project_utils import get_project_root
from iterative.service.utils.streamlit_utils import find_streamlit_scripts
from iterative.ui.gpt_chat import main as gpt_chat_main

current_project_root_dir = get_project_root()
current_project_name = current_project_root_dir.split('/')[-1]

iterative_project_name = f'PROJECT: {current_project_name}'
st.sidebar.image('https://res.cloudinary.com/dzmqies6h/image/upload/v1703108122/DALL_E_2023-12-20_15.35.12_-_Create_an_epic_dark_ink_scape_depicting_a_solar_system_with_a_focus_on_the_vastness_and_majesty_of_space._The_style_should_be_dramatic_and_artistic_jsyuon.png')
st.sidebar.title('Iterative')

app_mode = st.sidebar.selectbox('Choose the app mode', [iterative_project_name, 'ChatGPT Clone',  ])

if app_mode == 'ChatGPT Clone':
    gpt_chat_main()

elif app_mode == iterative_project_name:
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