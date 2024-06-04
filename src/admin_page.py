from google.cloud import pubsub_v1
from utils import download_data

import streamlit as st
import params as p
import json
import pandas as pd


publisher = pubsub_v1.PublisherClient()
train_topic_path = publisher.topic_path(p.PROJECT_ID, p.TRAIN_TOPIC_ID)
predict_topic_path = publisher.topic_path(p.PROJECT_ID, p.PREDICT_TOPIC_ID)


@st.cache_data(ttl=60*15)
def get_training_summaries():
    training_summaries = {}
    for aux_file in p.AUX_FILES_TO_DOWNLOAD:
        download_data(p.BUCKET_NAME, **aux_file)

        destination_file_name = aux_file['destination_file_name']
        with open(destination_file_name, 'r') as f:
            training_summaries[p.TRAINING_SUMMARY_MAP[destination_file_name]] = json.load(f)

    return training_summaries


def display_page(city_state_predictions, state_predictions, selected_filters):
    """
    Displays the page based on the context.
    """

    st.markdown('## Admin Page')

    st.markdown('### City State Predictions')    
    st.dataframe(city_state_predictions.drop(columns=['predicted_flag']), use_container_width=True, hide_index=True)

    st.markdown('### State Predictions')
    st.dataframe(state_predictions.drop(columns=['predicted_flag']), use_container_width=True, hide_index=True)

    st.markdown('### Pipelines')
    col_1, col_2 = st.columns(2)

    col_1.markdown('##### Train model')
    if col_1.button('Trigger pipeline', key='train_pipeline_trigger'):
        col_1.info('Update Datasets and Train Model triggered.')
        future = publisher.publish(
            train_topic_path, b"Update Datasets and Train Model", origin="python-sample", username="gcp"
        )
        print(future.result())

    col_2.markdown('##### Predict')
    if col_2.button('Trigger pipeline', key='predict_pipeline_trigger'):
        col_2.info('Predict pipeline triggered.')
        future = publisher.publish(
            predict_topic_path, b"Predict", origin="python-sample", username="gcp"
        )
        print(future.result())

    st.markdown('### Training Summary')

    training_summaries = get_training_summaries()

    st.markdown('#### Zip Level')
    zip_execution_date = training_summaries['zip_level']['execution_date']
    zip_roc_auc = training_summaries['zip_level']['roc_auc_score']
    zip_classification_report = training_summaries['zip_level']['classification_report']
    zip_classification_report_df = pd.DataFrame(zip_classification_report).transpose()

    st.markdown(f'- **Execution Date**: {zip_execution_date}')
    st.markdown(f'- **ROC AUC**: {zip_roc_auc}')
    st.dataframe(zip_classification_report_df, use_container_width=True)

    st.markdown('#### State Level')
    state_execution_date = training_summaries['state_level']['execution_date']
    state_roc_auc = training_summaries['state_level']['roc_auc_score']
    state_classification_report = training_summaries['state_level']['classification_report']
    state_classification_report_df = pd.DataFrame(state_classification_report).transpose()
    
    st.markdown(f'- **Execution Date**: {state_execution_date}')
    st.markdown(f'- **ROC AUC**: {state_roc_auc}')
    st.dataframe(state_classification_report_df, use_container_width=True)
