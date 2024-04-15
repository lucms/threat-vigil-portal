import streamlit as st
from google.cloud import pubsub_v1
import params as p


publisher = pubsub_v1.PublisherClient()
train_topic_path = publisher.topic_path(p.PROJECT_ID, p.TRAIN_TOPIC_ID)
predict_topic_path = publisher.topic_path(p.PROJECT_ID, p.PREDICT_TOPIC_ID)


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
    
    st.markdown('#### Train model')
    if st.button('Trigger pipeline', key='train_pipeline_trigger'):
        st.info('Update Datasets and Train Model triggered.')
        future = publisher.publish(
            train_topic_path, b"Update Datasets and Train Model", origin="python-sample", username="gcp"
        )
        print(future.result())

    st.markdown('#### Predict')
    if st.button('Trigger pipeline', key='predict_pipeline_trigger'):
        st.info('Predict pipeline triggered.')
        future = publisher.publish(
            predict_topic_path, b"Predict", origin="python-sample", username="gcp"
        )
        print(future.result())
