from params import *
from google.cloud import storage
import streamlit as st
import pandas as pd
import home_page
import search_page
import admin_page


@st.cache_data(ttl=60*15)
def load_datasets():
    """
    Loads datasets from cloud storage.
    """
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(BUCKET_NAME)
    
    datasets = {}
    for dataset in DATASETS:
        dataset_name = dataset['name']

        blob = bucket.blob(dataset['blob'])
    
        # Download file and read as pickle
        local_filename = LOCAL_FILENAME.format(dataset=dataset_name)
        blob.download_to_filename(local_filename)

        # Loads dataset as pandas dataframe
        datasets[dataset_name] = (
            pd.read_csv(local_filename)
            .sort_values(DATASET_SORT_COLUMNS[dataset_name])
        )

    return datasets


def display_sidebar(datasets):

    page_names = PAGE_NAMES
    if st.session_state.user_email not in ADMIN_EMAILS:
        page_names = [
            'Home',
            'Gun Violence Threat Assessment'
        ]

    selected_page = st.sidebar.radio(
        'Select a page',
        page_names
    )

    if selected_page == 'Gun Violence Threat Assessment':

        states = datasets['city_data']['state_name'].sort_values().unique()

        state = st.sidebar.selectbox(
            'Select a state',
            states
        )

        cities = datasets['city_data'].query(
            f'state_name == "{state}"'
        )['city'].sort_values().unique()

        city = st.sidebar.selectbox(
            'Select a city',
            cities
        )

    elif selected_page == 'Admin Page':

        toggle_city_state = st.sidebar.toggle('Filter by city and state', False)

        if toggle_city_state:
            city = st.sidebar.selectbox(
                'Select a city',
                datasets['base_data']['city'].unique()
            )

            state = st.sidebar.selectbox(
                'Select a state',
                datasets['base_data']['state'].unique()
            )
        
        else:
            city = None
            state = None
        
    else:
        city = None
        state = None

    selected_filters = {
        'city': city,
        'state': state
    }

    return selected_filters, selected_page


def filter_datasets(datasets, selected_filters):
    """
    Filters datasets based on the context.
    """

    city = selected_filters['city']
    state = selected_filters['state']

    if city is None or state is None:
        return datasets

    city_state_predictions_df = datasets['city_state_predictions'].query(
        f'city == "{city}" and state == "{state}"'
    )

    state_predictions_df = datasets['state_predictions'].query(
        f'state == "{state}"'
    )

    base_data_df = datasets['base_data'].query(
        f'city == "{city}" and state == "{state}"'
    )

    filtered_datasets = {
        'city_state_predictions': city_state_predictions_df,
        'state_predictions': state_predictions_df,
        'base_data': base_data_df
    }

    return filtered_datasets


def load_page(selected_page, datasets, filtered_datasets, selected_filters):
    """
    Loads the page based on the context.
    """
    if selected_page == 'Home':
        return home_page.display_page(
            filtered_datasets['city_state_predictions'],
            filtered_datasets['state_predictions'],
            selected_filters
        )
    
    elif selected_page == 'Gun Violence Threat Assessment':
        return search_page.display_page(
            filtered_datasets['city_state_predictions'],
            filtered_datasets['state_predictions'],
            filtered_datasets['base_data'],
            datasets['base_data'],
            selected_filters
        )
    
    elif selected_page == 'Admin Page':
        return admin_page.display_page(
            filtered_datasets['city_state_predictions'],
            filtered_datasets['state_predictions'],
            selected_filters
        )
