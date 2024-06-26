from google.cloud import secretmanager
from google.cloud import storage
from httpx_oauth.clients.google import GoogleOAuth2
from params import *
from datetime import datetime, timedelta
import streamlit as st
import json
import asyncio
import logging
import time
import requests


# decorator function to measure execution time
def time_this(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f'INFO:: {func.__name__} took {end - start} seconds')
        return result
    return wrapper


def access_secret_version(secret_id, project_id, version_id="latest"):
    """
    Access the payload for the given secret version if one exists. The version
    can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
    """

    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    return response.payload.data.decode("UTF-8")


def fetch_oauth_client_data():
    return json.loads(access_secret_version(OAUTH_CLIENT_SECRET, SECRET_PROJECT_ID))


def fetch_hubspot_api_key():
    return access_secret_version(HUBSPOT_API_SECRET, SECRET_PROJECT_ID)


async def write_authorization_url(client,
                                  redirect_uri,
                                  state=None):
    authorization_url = await client.get_authorization_url(
        redirect_uri,
        scope=["profile", "email"],
        extras_params={"access_type": "offline"},
        state=state
    )
    return authorization_url


async def write_access_token(client,
                             redirect_uri,
                             code):
    token = await client.get_access_token(code, redirect_uri)
    return token


async def get_email(client,
                    token):
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email


def validate_hubspot_user(email):

    api_key = fetch_hubspot_api_key()
    HEADERS = {
        'Authorization': f'Bearer {api_key}',
    }

    # First, search if profile exists
    list_profile_url = f'{BASE_URL}/contacts/search'
    data = {
        'filters': [
            {
                'propertyName': 'email',
                'operator': 'EQ',
                'value': email
            }
        ],
        "properties": [
            "createdate", "email", "firstname", 
            "lastname", "hs_object_id", "squarespace_subscriber"
        ]
    }

    response = requests.post(list_profile_url, headers=HEADERS, json=data)
    response_json = response.json()

    results = response_json.get('results', [])

    if len(results) == 0:
        return False
    
    # Check if it's a Squarespace subscriber
    profile = results[0]
    is_squarespace_subscriber = profile['properties'].get('squarespace_subscriber', None)

    if is_squarespace_subscriber is not None:
        if int(is_squarespace_subscriber) == 1:
            return True

    # After, check if profile has active subscription
    profile_id = profile['id']
    search_subscription_url = f'{BASE_URL}/subscriptions/search'
    data = {
        'filters': [
            {
                "propertyName": "associations.contact",
                "operator": "EQ",
                "value": profile_id
            },
            {
                "propertyName": "hs_status",
                "operator": "EQ",
                "value": "active"
            }
        ]
    }

    subscription_response = requests.post(search_subscription_url, headers=HEADERS, json=data)
    subscription_response_json = subscription_response.json().get('results', [])
    has_active_subscription = len(subscription_response_json) > 0
    
    return has_active_subscription


def authenticate_user_oauth(main_function):
    client_data = fetch_oauth_client_data()
    client_id = client_data['client_id']
    client_secret = client_data['client_secret']
    redirect_uri = client_data['redirect_uris'][ENV]


    state_param = st.query_params.to_dict().get('state', [None])[0]

    client = GoogleOAuth2(client_id, client_secret)
    authorization_url = asyncio.run(
        write_authorization_url(client=client,
                                redirect_uri=redirect_uri[-1],
                                state=state_param)
    )

    if 'token' not in st.session_state:
        st.session_state['token'] = None

    if st.session_state['token'] is None:
        try:
            code = st.query_params.to_dict()['code']
        except:
            st.markdown(f'''# Please, login at [this link]({authorization_url})''')
        else:
            # Verify token is correct:
            try:
                token = asyncio.run(
                    write_access_token(client=client,
                                       redirect_uri=redirect_uri,
                                       code=code)
                )
            except:
                st.markdown(f'''# Please, login again [this link]({authorization_url})''')
            else:
                # Check if token has expired:
                if token.is_expired():
                    if token.is_expired():
                        st.markdown(f'''# Please, login again [this link]({authorization_url})''')

                else:
                    st.session_state.token = token

                    user_id, user_email = asyncio.run(
                        get_email(client=client,
                                  token=token['access_token'])
                    )
                    st.session_state.user_id = user_id
                    st.session_state.user_email = user_email
                    logging.info(f'INFO:: Session started for user {user_email}')

                    if user_email not in ADMIN_EMAILS:
                        st.markdown('# Sorry, the Threat Vigil Portal is not available for general access yet.')
                    else:
                        main_function()

    else:
        if st.session_state.user_email not in ADMIN_EMAILS:
            st.markdown('# Sorry, the Threat Vigil Portal is not available for general access yet.')
        else:
            main_function()


def authenticate_user(main_function):

    if st.session_state.get('user_email') is not None:
        main_function()
    
    else:
        placeholder = st.empty()
        with placeholder.form(key='email_form'):
            email = st.text_input('Email')
            submit_button = st.form_submit_button('Submit')


        if submit_button:
            if email in ADMIN_EMAILS:
                authenticate_user_oauth(main_function)

            else:
                valid_email = validate_hubspot_user(email)
                if valid_email:
                    st.session_state.user_email = email
                    st.session_state.user_id = email
                    logging.info(f'INFO:: Session started for user {email}')
                    placeholder.empty()
                    main_function()
                else:
                    st.error('Invalid email. Please, try again.')


def download_data(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print(
        "Blob {} downloaded to {}.".format(
            source_blob_name, destination_file_name
        )
    )
