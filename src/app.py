import app_flow
import logging
import utils
import streamlit as st


st.set_page_config(
    page_title="Threat Vigil Portal",
)


def main():

    st.markdown('Mobile Users: Click on the > to open the sidebar, and the x to close it.')
    st.sidebar.markdown('Mobile Users: Click on the > to open the sidebar, and the x to close it.')
    datasets = app_flow.load_datasets()

    selected_filters, selected_page = app_flow.display_sidebar(datasets)

    filtered_datasets = app_flow.filter_datasets(datasets, selected_filters)

    app_flow.load_page(selected_page, datasets, filtered_datasets, selected_filters)
    logging.info(f'INFO:: displayed page {selected_page}')


if __name__ == '__main__':
    utils.authenticate_user(main)
    #st.session_state.user_email = 'lucas.miura.threat.vigil@gmail.com'
    #main()