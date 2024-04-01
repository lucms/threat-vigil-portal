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
    for dataset_name in DATASET_NAMES:
        blob = bucket.blob(DATASETS_BLOB.format(dataset=dataset_name))
    
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

    selected_page = st.sidebar.radio(
        'Select a page',
        PAGE_NAMES
    )

    if selected_page == 'Search Page':
        state = st.sidebar.selectbox(
            'Select a state',
            datasets['city_state_predictions']['state'].unique()
        )

        cities = datasets['city_state_predictions'].query(
            f'state == "{state}"'
        )['city'].unique()

        city = st.sidebar.selectbox(
            'Select a city',
            cities
        )

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

    filtered_datasets = {
        'city_state_predictions': city_state_predictions_df,
        'state_predictions': state_predictions_df
    }

    return filtered_datasets


def load_page(selected_page, filtered_datasets, selected_filters):
    """
    Loads the page based on the context.
    """
    if selected_page == 'Home':
        return home_page.display_page(
            filtered_datasets['city_state_predictions'],
            filtered_datasets['state_predictions'],
            selected_filters
        )
    
    elif selected_page == 'Search Page':
        return search_page.display_page(
            filtered_datasets['city_state_predictions'],
            filtered_datasets['state_predictions'],
            selected_filters
        )
    
    elif selected_page == 'Admin Page':
        return admin_page.display_page(
            filtered_datasets['city_state_predictions'],
            filtered_datasets['state_predictions'],
            selected_filters
        )
