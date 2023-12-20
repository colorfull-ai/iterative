# Main Streamlit Interface
import streamlit as st
from iterative.service.utils.project_utils import get_project_root
from iterative.service.utils.streamlit_utils import find_streamlit_scripts
from iterative.ui.gpt_chat import main as gpt_chat_main
from iterative.ui.assistant_chat import main as assistant_chat_main

current_project_root_dir = get_project_root()
current_project_name = current_project_root_dir.split('/')[-1]

iterative_project_name = f'PROJECT: {current_project_name}'
st.sidebar.image('https://res.cloudinary.com/dzmqies6h/image/upload/v1703100641/DALL_E_2023-12-20_13.30.29_-_Create_a_movie_poster-style_image_titled_Iterative_with_the_subtitle_AI_Framework_._The_background_should_be_a_vibrant_colorful_ink_scape_depicti_baar7u.png')
# streamlit header logo image instead of sidebar image
# st.image('https://res.cloudinary.com/dzmqies6h/image/upload/v1703100641/DALL_E_2023-12-20_13.30.29_-_Create_a_movie_poster-style_image_titled_Iterative_with_the_subtitle_AI_Framework_._The_background_should_be_a_vibrant_colorful_ink_scape_depicti_baar7u.png')
st.sidebar.title('Iterative')

app_mode = st.sidebar.selectbox('Choose the app mode', [iterative_project_name, 'ChatGPT Clone', 'Assistant', ])

if app_mode == 'ChatGPT Clone':
    gpt_chat_main()

elif app_mode == 'Assistant':
    assistant_chat_main()
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