import streamlit as st


def display_page(city_state_predictions, state_predictions, selected_filters):
    """
    Displays the page based on the context.
    """
    
    st.markdown('# Threat Vigil Portal')

    st.markdown('''
    This portal provides a way to monitor the threat level of mass shooting incidents in the United States.
    ''')