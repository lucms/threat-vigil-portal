import streamlit as st


def display_page(zip_predictions, state_predictions, selected_filters):
    """
    Displays the page based on the context.
    """
    
    st.markdown('# Threat Vigil Portal')

    st.markdown('''
    This portal provides a way to monitor the threat level of gun violence incidents in the United States.
    ''')

    st.markdown('## Methodology')
    st.markdown('''
        Threat Vigil harvests news, data from crime databases and other sources continually.  \
        It then processes the data through its proprietary machine learning program to predict the locations \
        of the next likely gun violence event in the coming month.  \
        As new information is collected, those predictions can change over the course of days or weeks, so it is advisable to check often.    
    ''')
