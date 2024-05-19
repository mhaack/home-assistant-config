from datetime import datetime

import requests
from bs4 import BeautifulSoup
from waste_collection_schedule import Collection  # type: ignore[attr-defined]

TITLE = "North Yorkshire Council - Selby"
DESCRIPTION = "Source for North Yorkshire Council - Selby."
URL = "https://northyorks.gov.uk"
TEST_CASES = {
    "100052176620": {"uprn": 100052176620},
    "10013454353": {"uprn": "10013454353"},
}


ICON_MAP = {
    "Household": "mdi:trash-can",
    "Garden": "mdi:leaf",
    "Recycling": "mdi:recycle",
}


API_URL = "https://www.northyorks.gov.uk/bin-calendar/Selby/results/{uprn}/ajax?_wrapper_format=drupal_ajax"


class Source:
    def __init__(self, uprn: str | int):
        self._uprn: str = str(uprn)

    def fetch(self):
        r = requests.post(API_URL.format(uprn=self._uprn))
        r.raise_for_status()

        html = None
        for res in r.json():
            if "data" in res and isinstance(res["data"], str):
                html = res["data"]
                break
        if not html or "Unfortunately we were unable to find your property" in html:
            raise Exception("No data found, invalid UPRN?")
        soup = BeautifulSoup(html, "html.parser")

        rows = (
            soup.find("div", id="upcoming-collection")
            .find("table")
            .find("tbody")
            .find_all("tr")
        )

        entries = []
        for row in rows:
            tds = row.find_all("td")

            if not tds or len(tds) < 3:
                continue
            date_str = tds[0].text
            date = datetime.strptime(date_str, "%d %B %Y").date()
            bin_types = [br.next_sibling.strip() for br in tds[2].find_all("i")]
            if not bin_types:
                continue

            for bin_type in bin_types:
                icon = ICON_MAP.get(bin_type.split(" ")[0])
                entries.append(Collection(date=date, t=bin_type, icon=icon))

        return entries
