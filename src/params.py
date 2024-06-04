import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID =  os.getenv('PROJECT_ID')

if PROJECT_ID is None:
    raise ValueError('PROJECT_ID environment variable not set.')

if PROJECT_ID == 'threat-vigil-prod':
    BUCKET_NAME = 'threat-vigil-tmp-files'
    OAUTH_CLIENT_SECRET = "threat-vigil-portal-oauth-client-prod"
    ENV = 'prod'
    SECRET_PROJECT_ID = 964526035193

else:
    BUCKET_NAME = 'threat-vigil-stg-tmp-files'
    OAUTH_CLIENT_SECRET = "threat-vigil-portal-oauth-client-stg"
    ENV = 'stg'
    SECRET_PROJECT_ID = 531745979735
    
TRAIN_TOPIC_ID = 'elt-ml-train-topic'
PREDICT_TOPIC_ID = 'ml-predict-topic'

HUBSPOT_API_SECRET = 'hubspot-api-key'

BASE_URL = f'https://api.hubapi.com/crm/v3/objects'
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
ACCOUNT_MIN_TIME = 365


EMPTY_PAGE_MESSAGE = """\
## Nothing to display

If you think this is an error, please contact the system admin at info@threatvigil.com.
"""

ADMIN_EMAILS = [
    'lucas.miura.threat.vigil@gmail.com',
    'threatvigil@gmail.com'
]

DEFAULT_ENCODING = 'iso-8859-1'
LOCAL_FILENAME = './{dataset}.csv'

DATASETS = [
    {
        'name': 'zip_predictions',
        'blob': 'predictions/zip_city_state_predictions.csv'
    },
    {
        'name': 'state_predictions',
        'blob': 'predictions/state_predictions.csv'
    },
    {
        'name': 'base_data',
        'blob': 'data/pipelines/gva_weather_guns_zip_level.csv'
    },
    {
        'name': 'city_data',
        'blob': 'data/city_data.csv'
    }
]

TRAINING_SUMMARY_ZIP_LEVEL_FILENAME = 'training_summary_zip_level.json'
TRAINING_SUMMARY_ZIP_LEVEL_FILE = f'./{TRAINING_SUMMARY_ZIP_LEVEL_FILENAME}'
TRAINING_SUMMARY_ZIP_LEVEL_BLOB = f'training_summaries/{TRAINING_SUMMARY_ZIP_LEVEL_FILENAME}'

TRAINING_SUMMARY_STATE_LEVEL_FILENAME = 'training_summary_state_level.json'
TRAINING_SUMMARY_STATE_LEVEL_FILE = f'./{TRAINING_SUMMARY_STATE_LEVEL_FILENAME}'
TRAINING_SUMMARY_STATE_LEVEL_BLOB = f'training_summaries/{TRAINING_SUMMARY_STATE_LEVEL_FILENAME}'


AUX_FILES_TO_DOWNLOAD = [
    {
        'source_blob_name': TRAINING_SUMMARY_ZIP_LEVEL_BLOB,
        'destination_file_name': TRAINING_SUMMARY_ZIP_LEVEL_FILE,
    },
    {
        'source_blob_name': TRAINING_SUMMARY_STATE_LEVEL_BLOB,
        'destination_file_name': TRAINING_SUMMARY_STATE_LEVEL_FILE
    }
]

TRAINING_SUMMARY_MAP = {
    TRAINING_SUMMARY_ZIP_LEVEL_FILE: 'zip_level',
    TRAINING_SUMMARY_STATE_LEVEL_FILE: 'state_level'
}

DATASET_DTYPES = {
    'zip_predictions': {
        'zip_code': str
    },
    'state_predictions': None,
    'base_data': {
        'zip_code': str
    },
    'city_data': None
}

PAGE_NAMES = [
    'Home',
    'Gun Violence Threat Assessment',
    'Admin Page'
]

DATASET_SORT_COLUMNS = {
    'zip_predictions': ['yearmonth', 'state', 'city', 'zip_code'],
    'state_predictions': ['yearmonth', 'state'],
    'base_data': ['yearmonth', 'state', 'city', 'zip_code'],
    'city_data': ['city']
}

PREDICTION_DESCRIPTIONS = {
    'Very Low': '''\
This category suggests that the likelihood of the predicted event occurring \
is relatively small, based on the historical data and patterns the model has learned. \
While it's not impossible for the event to happen, the model indicates that under current \
and historical conditions, it's unlikely.
''',
    'Low': '''\
This category suggests that the likelihood of the predicted event occurring \
is relatively small, based on the historical data and patterns the model has learned. \
While it's not impossible for the event to happen, the model indicates that under current \
and historical conditions, it's unlikely.
''',
    'Medium Low': '''\
This output indicates a slightly higher likelihood compared to the low probability category, \
but still remains on the lower end of the probability spectrum. It means that while there are \
some indicators pointing towards the occurrence of the event, they aren't strong or consistent \
enough to warrant a higher probability rating.
''',
    'Medium': '''\
This is a middle-ground prediction, suggesting that the event has an average chance of occurring. \
This implies that the historical data and model learning show a balanced mix of indicators, both for \
and against the occurrence of the event.
''',
    'Medium High': '''\
In this category, the likelihood of the event occurring is above average. This suggests that a \
significant number of indicators or patterns in the historical data lean towards the event happening. \
However, there are still some factors that introduce uncertainty.
''',
    'High': '''\
This is the highest level of certainty provided by your program. It suggests that, according to the \
historical data and the learned patterns, the event is very likely to occur. The indicators and patterns \
in the data strongly point towards this outcome.
'''
}
