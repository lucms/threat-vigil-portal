from params import *
from google.cloud import storage
import streamlit as st
import pandas as pd
import home_page
import search_page
import admin_page
import re


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
            pd.read_csv(local_filename, dtype=DATASET_DTYPES[dataset_name])
            .sort_values(DATASET_SORT_COLUMNS[dataset_name])
        )

    datasets['zip_predictions']['zip_code'] = datasets['zip_predictions']['zip_code'].astype(str)

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

        with st.sidebar.form(key='search_form') as form:

            #TODO validate zip code
            zip = st.text_input(
                'Zip code',
            )

            submit_button = st.form_submit_button('Submit')
            st.markdown('If the provided zip code is invalid, only state predictions are valid.')
            if submit_button:
                st.session_state.search_form_submitted = True
                selected_filters = {
                    'zip': zip,
                    'city': city,
                    'state': state
                }

                return selected_filters, selected_page

    elif selected_page == 'Admin Page':

        toggle_city_state = st.sidebar.toggle('Filter by city and state', False)

        if not toggle_city_state:
            zip = None
            city = None
            state = None

            selected_filters = {
                'zip': zip,
                'city': city,
                'state': state
            }

            return selected_filters, selected_page

        if toggle_city_state:
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
            placeholder = st.sidebar.empty()
            with placeholder.form(key='admin_search_form') as form:

                zip = st.text_input(
                    'Zip code',
                )
                submit_button = st.form_submit_button('Submit')


                if submit_button:
                    selected_filters = {
                        'zip': zip,
                        'city': city,
                        'state': state
                    }

                    return selected_filters, selected_page

    else:
        zip = None
        city = None
        state = None

    selected_filters = {
        'zip': zip,
        'city': city,
        'state': state
    }

    return selected_filters, selected_page


def filter_datasets(datasets, selected_filters):
    """
    Filters datasets based on the context.
    """

    zip = selected_filters['zip']
    city = selected_filters['city']
    state = selected_filters['state']

    if zip is None or state is None:
        return datasets

    zip_predictions_df = datasets['zip_predictions'].query(
        f'zip_code == "{zip}" and state == "{state}" and city == "{city}"'
    )

    state_predictions_df = datasets['state_predictions'].query(
        f'state == "{state}"'
    )

    base_data_df = datasets['base_data'].query(
        f'zip_code == "{zip}" and state == "{state}" and city == "{city}"'
    )

    filtered_datasets = {
        'zip_predictions': zip_predictions_df,
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
            filtered_datasets['zip_predictions'],
            filtered_datasets['state_predictions'],
            selected_filters
        )
    
    elif selected_page == 'Gun Violence Threat Assessment':
        if not st.session_state.get('search_form_submitted', False):
            st.markdown('# Gun Violence Threat Assessment')

            st.markdown('Please submit a city, state and zip code to see results.')
            
        elif not re.match(r'(^\d{5}$)|(^\d{5}-\d{4}$)', selected_filters['zip']):
            st.error('Please enter a valid zip code')
            
        else:
            return search_page.display_page(
                filtered_datasets['zip_predictions'],
                filtered_datasets['state_predictions'],
                filtered_datasets['base_data'],
                datasets['base_data'],
                selected_filters
            )
    
    elif selected_page == 'Admin Page':
        return admin_page.display_page(
            filtered_datasets['zip_predictions'],
            filtered_datasets['state_predictions'],
            selected_filters
        )
