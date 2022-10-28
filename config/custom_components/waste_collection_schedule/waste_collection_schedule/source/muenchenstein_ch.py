import json
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from waste_collection_schedule import Collection  # type: ignore[attr-defined]

TITLE = "Abfallsammlung Münchenstein"
DESCRIPTION = "Source for Muenchenstein waste collection."
URL = "https://www.muenchenstein.ch/abfallsammlung"
TEST_CASES = {
    "Abfuhrkreis Ost": {"waste_district": "Abfuhrkreis Ost"},
    "Abfuhrkreis West": {"waste_district": "492"},
}


IconMap = {
    "kehricht": "mdi:trash-can",
    "hackseldienst": "mdi:leaf",
    "papierabfuhr": "mdi:newspaper-variant-multiple-outline",
    "kartonabfuhr": "mdi:package-variant",
    "altmetalle": "mdi:nail",
}


class Source:
    def __init__(self, waste_district):
        self._waste_district = waste_district

    def fetch(self):
        response = requests.get(URL)

        html = BeautifulSoup(response.text, "html.parser")

        table = html.find("table", attrs={"id": "icmsTable-abfallsammlung"})
        data = json.loads(table.attrs["data-entities"])

        entries = []
        for item in data["data"]:
            if (
                self._waste_district in item["abfallkreisIds"]
                or self._waste_district in item["abfallkreisNameList"]
            ):
                next_pickup = item["_anlassDate-sort"].split()[0]
                next_pickup_date = datetime.fromisoformat(next_pickup).date()

                waste_type = BeautifulSoup(item["name"], "html.parser").text
                waste_type_sorted = BeautifulSoup(item["name-sort"], "html.parser").text

                entries.append(
                    Collection(
                        date=next_pickup_date,
                        t=waste_type,
                        icon=IconMap.get(waste_type_sorted, "mdi:trash-can"),
                    )
                )

        # Collection of "Kehricht und Kleinsperrgut brennbar" are not listed with dates as events on website.
        # Instead it states the day of the week for each waste district: tuesday for east and friday for west
        # So we're going to set those collections programmatically for the next 4 occurrences
        weekday_collection = 2 if self._waste_district == 'Abfuhrkreis Ost' or self._waste_district == 491 else 4
        weekday_today = datetime.now().isoweekday()
        for x in range(4):
            days_to_pickup = (x * 7) + ((weekday_collection - weekday_today) % 7)
            next_pickup_date = (datetime.now() + timedelta(days=days_to_pickup)).date()
            waste_type = "Kehricht und Kleinsperrgut brennbar"

            entries.append(
                Collection(
                    date=next_pickup_date,
                    t=waste_type,
                    icon=IconMap.get(waste_type_sorted, "mdi:trash-can"),
                )
            )

        return entries
