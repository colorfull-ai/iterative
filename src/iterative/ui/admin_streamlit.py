import streamlit as st
from streamlit_chat import message
from iterative import ask_assistant

# Initialize Streamlit session state
if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

def on_input_change():
    user_input = st.session_state.user_input
    st.session_state.past.append(user_input)

    # Get response from AI assistant
    response = ask_assistant(user_input)
    st.session_state.generated.append(response)

def on_btn_click():
    del st.session_state.past[:]
    del st.session_state.generated[:]

st.title("Chat with AI")

chat_placeholder = st.empty()

with chat_placeholder.container():    
    for i in range(len(st.session_state.generated)):                
        message(st.session_state.past[i], is_user=True, key=f"{i}_user")
        message(st.session_state.generated[i], key=f"{i}")

    st.button("Clear message", on_click=on_btn_click)

with st.container():
    st.text_input("User Input:", on_change=on_input_change, key="user_input")
