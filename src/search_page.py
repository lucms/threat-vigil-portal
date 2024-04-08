import streamlit as st
import pandas as pd
from params import *


def display_city_page(city_state_predictions, state_predictions, base_data, unfiltered_base_data, selected_filters):
    """
    Displays the page based on the context.
    """
    city = selected_filters['city']
    state = selected_filters['state']
    
    st.markdown(f'# Mass shooting threat assessment')
    st.markdown(f'## {city}, {state}')


    st.markdown('''
    Assess the probability of a mass shooting incident happening in the next 30 days.
    ''')

    prediction = city_state_predictions['prediction'].values[0].round(3)

    prediction_proba_string = f'{prediction * 100:.1f}%'
    
    label = city_state_predictions['predicted_label'].values[0]

    col1, col2 = st.columns(2)
    col1.metric("Threat level", label)
    col2.metric("Probability", prediction_proba_string)

    prediction_yearmonth = city_state_predictions['yearmonth'].values[0]
    prediction_date = pd.to_datetime(prediction_yearmonth, format='%Y-%m')
    prediction_date_str = prediction_date.strftime('%B %Y')
    st.markdown(f'Predictions valid for {prediction_date_str}.')

    st.markdown(PREDICTION_DESCRIPTIONS[label])

    # Add a call to action for medium high and high threats
    if label in ('Medium High', 'High'):
        CALL_TO_ACTION = 'Please be cautious and report any suspicious activity to the authorities.'
        st.markdown(CALL_TO_ACTION)

    # Next, displaying recent mass shootings    
    NUM_DISPLAY_YEARMONTHS = 2
    last_yearmonth = prediction_date - pd.DateOffset(months=NUM_DISPLAY_YEARMONTHS)
    last_yearmonth = last_yearmonth.strftime('%Y-%m')
    
    last_shootings_df = unfiltered_base_data.query(f'\
        yearmonth >= "{last_yearmonth}" and state == "{state}" and\
        counts > 0\
    ')

    DISPLAY_COLS = ['yearmonth', 'city', 'counts']

    last_shootings_df['yearmonth'] = pd.to_datetime(last_shootings_df['yearmonth'], format='%Y-%m').dt.strftime('%B %Y')

    last_shootings_df = (last_shootings_df
        [DISPLAY_COLS]
        .sort_values('yearmonth', ascending=False)
        .rename(columns={
            'yearmonth': 'Date',
            'city': 'City',
            'counts': 'Number of mass shootings'
        })
    )

    st.markdown('## Recent mass shootings')

    if not last_shootings_df.empty:
        st.markdown(f'List of recent mass shootings in {city}, {state}.')
        st.dataframe(last_shootings_df, use_container_width=True)
    else:
        st.markdown(f'There were no recent mass shootings in our database for {city}, {state}.')


def display_state_page(city_state_predictions, state_predictions, base_data, unfiltered_base_data, selected_filters):
    """
    Displays the page based on the context.
    """

    state = selected_filters['state']
    
    st.markdown(f'# Mass shooting threat assessment')
    
    city = selected_filters['city']
    st.markdown(f'''\
        Unfortunately, there isn't enough historical data to provide an accurate prediction for {city}, {state}.
        However, we can provide a prediction for the state of {state}.
    ''')
    
    st.markdown(f'## {state}')


    st.markdown('''
    Assess the probability of a mass shooting incident happening in the next 30 days.
    ''')

    prediction = state_predictions['prediction'].values[0].round(3)

    prediction_proba_string = f'{prediction * 100:.1f}%'
    
    label = None
    call_to_action = None
    if prediction < 0.1:
        label = 'Low'
    elif prediction < 0.3:
        label = 'Medium Low'
    elif prediction < 0.6:
        label = 'Medium'
    elif prediction < 0.85:
        label = 'Medium High'
        call_to_action = 'Please be cautious and report any suspicious activity to the authorities.'
    else:
        label = 'High'
        call_to_action = 'Please be cautious and report any suspicious activity to the authorities.'

    col1, col2 = st.columns(2)
    col1.metric("Threat level", label)
    col2.metric("Probability", prediction_proba_string)

    prediction_yearmonth = state_predictions['yearmonth'].values[0]
    prediction_date = pd.to_datetime(prediction_yearmonth, format='%Y-%m')
    prediction_date_str = prediction_date.strftime('%B %Y')
    st.markdown(f'Predictions valid for {prediction_date_str}.')
    
    st.markdown(PREDICTION_DESCRIPTIONS[label])

    if call_to_action is not None:
        st.markdown(call_to_action)


    # Next, display recent mass shootings
    NUM_DISPLAY_YEARMONTHS = 2
    last_yearmonth = prediction_date - pd.DateOffset(months=NUM_DISPLAY_YEARMONTHS)
    last_yearmonth = last_yearmonth.strftime('%Y-%m')
    
    st.text(last_yearmonth)
    last_shootings_df = unfiltered_base_data.query(f'\
        yearmonth >= "{last_yearmonth}" and state == "{state}" and\
        counts > 0\
    ')

    DISPLAY_COLS = ['yearmonth', 'city', 'counts']

    last_shootings_df['yearmonth'] = pd.to_datetime(last_shootings_df['yearmonth'], format='%Y-%m').dt.strftime('%B %Y')

    last_shootings_df = (last_shootings_df
        [DISPLAY_COLS]
        .sort_values('yearmonth', ascending=False)
        .rename(columns={
            'yearmonth': 'Date',
            'city': 'City',
            'counts': 'Number of mass shootings'
        })
    )

    st.markdown('## Recent mass shootings')
    if not last_shootings_df.empty:
        st.markdown(f'List of recent mass shootings in {state}.')
        st.dataframe(last_shootings_df, use_container_width=True)
    else:
        st.markdown(f'There were no recent mass shootings in our database for {state}.')


def display_page(city_state_predictions, state_predictions, base_data, unfiltered_base_data, selected_filters):
    """
    Displays the page based on the context.
    """
    if city_state_predictions.empty:
        display_state_page(
            city_state_predictions, 
            state_predictions, 
            base_data, 
            unfiltered_base_data,
            selected_filters
        )
    else:
        display_city_page(
            city_state_predictions, 
            state_predictions, 
            base_data,
            unfiltered_base_data,
            selected_filters
        )
