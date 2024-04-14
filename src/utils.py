from google.cloud import secretmanager
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


def fetch_squarespace_api_key():
    return access_secret_version(SQUARESPACE_API_SECRET, SECRET_PROJECT_ID)


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


def validate_squarespace_user(email):
    api_key = fetch_squarespace_api_key()
    search_url = SEARCH_URL_TEMPLATE.format(f=f'email,{email}')

    HEADERS = {
        'Authorization': f'Bearer {api_key}',
    }

    response = requests.get(search_url, headers=HEADERS)

    response_json = response.json()['profiles']

    if len(response_json) == 0:
        return False
    
    profile = response_json[0]
    profile_has_active_plan = datetime.strptime(profile['createdOn'], DATETIME_FORMAT) >= (datetime.now() - timedelta(days=ACCOUNT_MIN_TIME))
    profile_has_ccount = profile['hasAccount'] == True

    profile_is_valid = profile_has_active_plan and profile_has_ccount

    return profile_is_valid


def authenticate_user_oauth(main_function):
    client_data = fetch_oauth_client_data()
    client_id = client_data['client_id']
    client_secret = client_data['client_secret']
    redirect_uri = client_data['redirect_uris'][ENV]

    print(redirect_uri)

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
                    valid_email = validate_squarespace_user(email)
                    if valid_email:
                        st.session_state.user_email = email
                        st.session_state.user_id = email
                        logging.info(f'INFO:: Session started for user {email}')
                        placeholder.empty()
                        main_function()
                    else:
                        st.error('Invalid email. Please, try again.')