import streamlit as st


def display_page(city_state_predictions, state_predictions, selected_filters):
    """
    Displays the page based on the context.
    """

    st.markdown('## Admin Page')

    st.markdown('### City State Predictions')    
    st.dataframe(city_state_predictions.drop(columns=['predicted_flag']), use_container_width=True, hide_index=True)

    st.markdown('### State Predictions')
    st.dataframe(state_predictions.drop(columns=['predicted_flag']), use_container_width=True, hide_index=True)
