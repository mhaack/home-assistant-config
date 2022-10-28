import logging
from datetime import datetime
import re
import requests
# These lines are needed to suppress the InsecureRequestWarning resulting from the POST verify=False option
# With verify=True the POST fails due to a SSLCertVerificationError.
import urllib3
from waste_collection_schedule import Collection

urllib3.disable_warnings()
# The following links may provide a better way of dealing with this, as using verify=False is not ideal:
# https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
# https://urllib3.readthedocs.io/en/1.26.x/user-guide.html#ssl

_LOGGER = logging.getLogger(__name__)

TITLE = "newcastle.gov.uk"
DESCRIPTION = (
    """Source for waste collection services for Newcastle City Council"""
)
URL = "https://community.newcastle.gov.uk/my-neighbourhood/ajax/getBinsNew.php"
REGEX = "<strong>(Green|Blue|Brown) [bB]in \\((Domestic|Recycling|Garden)( Waste)?\\) details: <\\/strong><br\\/>" \
        "collection day : [a-zA-Z]*day<br\\/>" \
        "Next collection : ([0-9]{2}-[A-Za-z]+-[0-9]{4})"
ICONS = {
    "DOMESTIC": "mdi:trash-can",
    "RECYCLING": "mdi:recycle",
    "GARDEN": "mdi:leaf",
}

TEST_CASES = {
    "Test_001": {"uprn": "004510053797"},
    "Test_002": {"uprn": 4510053797}
}


class Source:
    def __init__(self, uprn=None):
        self._uprn = str(uprn).zfill(12)
        if not self._uprn:
            _LOGGER.error(
                "uprn must be provided in config"
            )
        self._uprn = self._uprn.zfill(12)
        self._session = requests.Session()

    def fetch(self):
        entries = []
        res = requests.get(f"{URL}?uprn={self._uprn}")
        collections = re.findall(REGEX, res.text)

        for collection in collections:
            collection_type = collection[1]
            collection_date = collection[3]
            entries.append(
                Collection(
                    date=datetime.strptime(collection_date, '%d-%b-%Y').date(),
                    t=collection_type,
                    icon=ICONS.get(collection_type.upper()),
                )
            )

        return entries
