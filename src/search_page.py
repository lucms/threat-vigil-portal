import streamlit as st
import pandas as pd
from params import *
from datetime import datetime


def display_zip_page(zip_predictions, state_predictions, base_data, unfiltered_base_data, selected_filters):
    """
    Displays the page based on the context.
    """
    zip = selected_filters['zip']
    city = selected_filters['city']
    state = selected_filters['state']
    
    st.markdown(f'# Gun Violence threat assessment')
    st.markdown(f'## {zip}, {city}, {state}')


    st.markdown('''
    Assess the probability of a gun violence incident happening in the next 30 days.
    ''')

    if zip_predictions.empty:
        prediction_proba_string = f'-'
        label = "Very Low"

        prediction_yearmonth = datetime.now().strftime('%Y-%m')
        prediction_date = pd.to_datetime(prediction_yearmonth, format='%Y-%m')  

    else:
        prediction = zip_predictions['prediction'].values[0].round(3)
        prediction_proba_string = f'{prediction * 100:.1f}%'
        label = zip_predictions['predicted_label'].values[0]
        
        prediction_yearmonth = zip_predictions['yearmonth'].values[0]
        prediction_date = pd.to_datetime(prediction_yearmonth, format='%Y-%m')
    
    st.markdown(f'Predictions valid for the next 30 days.')

    col1, col2 = st.columns(2)
    col1.metric("Threat level", label)
    col2.metric("Probability", prediction_proba_string)

    st.markdown(PREDICTION_DESCRIPTIONS[label])

    # Add a call to action for medium high and high threats
    if label in ('Medium High', 'High'):
        CALL_TO_ACTION = 'Please be cautious and report any suspicious activity to the authorities.'
        st.markdown(CALL_TO_ACTION)

    # Next, displaying recent gun violence incidents    
    NUM_DISPLAY_YEARMONTHS = 2
    last_yearmonth = prediction_date - pd.DateOffset(months=NUM_DISPLAY_YEARMONTHS)
    last_yearmonth = last_yearmonth.strftime('%Y-%m')
    
    last_shootings_df = unfiltered_base_data.query(f'\
        yearmonth >= "{last_yearmonth}" and state == "{state}" and city == "{city}" and\
        counts > 0\
    ')

    DISPLAY_COLS = ['counts', 'city']

    last_shootings_df = (last_shootings_df
        [DISPLAY_COLS]
        .groupby('city')
        .sum()
        .rename(columns={'counts':'Total gun violence incidents in the last two months'})
    )

    st.markdown('### Gun violence incidents in the last two months')
    if not last_shootings_df.empty:
        st.markdown(f'List of gun violence incidents in {city}, {state} in the last two months.')
        st.dataframe(last_shootings_df, use_container_width=True)
    else:
        st.markdown(f'There were no gun violence incidents in the last two months for {city}, {state} at our database.')


def display_state_page(zip_predictions, state_predictions, base_data, unfiltered_base_data, selected_filters):
    """
    Displays the page based on the context.
    """

    state = selected_filters['state']
    
    st.markdown(f'## State-wide threat assessment')
    st.markdown(f'## {state}')

    prediction = state_predictions['prediction'].values[0].round(3)
    prediction_proba_string = f'{prediction * 100:.1f}%'
    label = state_predictions['predicted_label'].values[0]

    col1, col2 = st.columns(2)
    col1.metric("Threat level", label)
    col2.metric("Probability", prediction_proba_string)

    prediction_yearmonth = state_predictions['yearmonth'].values[0]
    prediction_date = pd.to_datetime(prediction_yearmonth, format='%Y-%m')
    st.markdown(f'Predictions valid for the next 30 days.')
    
    st.markdown(PREDICTION_DESCRIPTIONS[label])

    # Add a call to action for medium high and high threats
    if label in ('Medium High', 'High'):
        CALL_TO_ACTION = 'Please be cautious and report any suspicious activity to the authorities.'
        st.markdown(CALL_TO_ACTION)


    # Next, display recent gun violence incidents
    NUM_DISPLAY_YEARMONTHS = 2
    last_yearmonth = prediction_date - pd.DateOffset(months=NUM_DISPLAY_YEARMONTHS)
    last_yearmonth = last_yearmonth.strftime('%Y-%m')
    
    last_shootings_df = unfiltered_base_data.query(f'\
        yearmonth >= "{last_yearmonth}" and state == "{state}" and\
        counts > 0\
    ')

    DISPLAY_COLS = ['city', 'counts']

    last_shootings_df = (last_shootings_df
        [DISPLAY_COLS]
        .groupby('city')
        ['counts']
        .sum()
        .rename('Total gun violence incidents in the last two months')
    )

    st.markdown('### Gun violence incidents in the last two months')
    if not last_shootings_df.empty:
        st.markdown(f'List of gun violence incidents in {state} in the last two months.')
        st.dataframe(last_shootings_df, use_container_width=True)
    else:
        st.markdown(f'There were no gun violence incidents in the last two months for {state} at our database.')


def display_page(zip_predictions, state_predictions, base_data, unfiltered_base_data, selected_filters):
    """
    Displays the page based on the context.
    """

    display_zip_page(
        zip_predictions, 
        state_predictions, 
        base_data,
        unfiltered_base_data,
        selected_filters
    )

    st.divider()

    display_state_page(
        zip_predictions, 
        state_predictions, 
        base_data, 
        unfiltered_base_data,
        selected_filters
    )
