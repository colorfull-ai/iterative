from iterative.actions.assistant_actions import ask_assistant, delete_files, get_assistant_info, set_docs_as_knowledge, update_assistant_tools_with_actions
from openai import OpenAI
import streamlit as st
import os


def main():
    from iterative.actions.assistant_actions import _get_configured_actions
    web_actions, cli_actions = _get_configured_actions()
    # Create a dropdown for selecting an action
    action_names = list(web_actions.keys())
    selected_action = st.selectbox("Select an action to execute", action_names)

    # Execute the selected action
    if st.button(f"Execute '{selected_action}'"):
        try:
            action_function = web_actions[selected_action].function
            # Execute the action (assuming no parameters required for simplicity)
            action_result = action_function()
            st.success(f"Executed action '{selected_action}'. Result: {action_result}")
        except Exception as e:
            st.error(f"Error executing action '{selected_action}': {str(e)}")

    st.title("Interactive AI Assistant")

    # Display assistant information
    if st.button('Show Assistant Info'):
        assistant_info = get_assistant_info()
        st.json(assistant_info)

    # Text input for user to type a message
    user_message = st.text_input("Enter your message to the Assistant:")

    # Button to send the message
    if st.button('Send Message'):
        if user_message:
            response = ask_assistant(user_message)
            st.write(response)
        else:
            st.error("Please enter a message.")

    # Additional functionalities
    if st.button('Update Assistant with Actions'):
        update_result = update_assistant_tools_with_actions()
        st.write(update_result)

    if st.button('Set Documents as Knowledge'):
        knowledge_result = set_docs_as_knowledge()
        st.write(knowledge_result)

    if st.button('Delete Files'):
        delete_files_result = delete_files()
        st.write(delete_files_result)
