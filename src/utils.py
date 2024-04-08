from google.cloud import secretmanager
from httpx_oauth.clients.google import GoogleOAuth2
from params import *
import streamlit as st
import json
import asyncio
import logging
import time


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


def authenticate_user(main_function):
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
