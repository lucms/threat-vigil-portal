env = 'prod'
BUCKET_NAME = "threat-vigil-tmp-files"
OAUTH_CLIENT_SECRET = "threat-vigil-portal-oauth-client"

EMPTY_PAGE_MESSAGE = """\
## Nothing to display

If you think this is an error, please contact the system admin at info@threatvigil.com.
"""

#TODO ADD
SECRET_PROJECT_ID = None

DEFAULT_ENCODING = 'iso-8859-1'
DATASETS_BLOB = 'predictions/{dataset}.csv'
LOCAL_FILENAME = './{dataset}.csv'

PAGE_NAMES = [
    'Home',
    'Search Page',
    'Admin Page'
]

DATASET_NAMES = [
    'city_state_predictions',
    'state_predictions'
]

DATASET_SORT_COLUMNS = {
    'city_state_predictions': ['yearmonth', 'state', 'city'],
    'state_predictions': ['yearmonth', 'state']
}

PREDICTION_DESCRIPTIONS = {
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