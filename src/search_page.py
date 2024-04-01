import streamlit as st
from params import *


def display_page(city_state_predictions, state_predictions, selected_filters):
    """
    Displays the page based on the context.
    """
    city = selected_filters['city']
    state = selected_filters['state']
    
    st.markdown(f'# Shooting probability for {city}, {state}')

    st.markdown('''
    This page shows the probability of a mass shooting incident happening in the next 30 days in the selected city.
    ''')

    prediction = city_state_predictions['prediction'].values[0].round(3)

    prediction_proba_string = f'{prediction * 100:.1f}%'
    st.markdown(f'## Probability: {prediction_proba_string}')
    
    label = None
    if prediction < 0.1:
        label = 'Low'
    elif prediction < 0.3:
        label = 'Medium Low'
    elif prediction < 0.6:
        label = 'Medium'
    elif prediction < 0.85:
        label = 'Medium High'
    else:
        label = 'High'
    
    st.markdown(f'## Threat Level: {label}')
    st.markdown(PREDICTION_DESCRIPTIONS[label])
