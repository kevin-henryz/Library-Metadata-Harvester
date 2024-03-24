import requests
import re
from ratelimit import limits, sleep_and_retry
import util.dictionaryValidationMethod as vd

from apis.baseAPI import BaseAPI


# The LOC API does not have a dedicated endpoint for fetching metadata by identifier, so we use the search API
# The API does not return ISBNs, so we return an empty list for ISBNs if the input is OCN
class LibraryOfCongressAPI(BaseAPI):
    def __init__(self):
        self.base_url = "https://www.loc.gov/search/"
        self.name = "LOC"
        self.catalog_data = {
            'ISBN': [],
            'OCN': '',
            'LCCN': [],
            'LCCN_Source': []
        }

    @sleep_and_retry
    @limits(calls=10, period=10)  # Allow 10 requests every 10 seconds for burst limit
    def fetch_metadata(self, identifier, input_type):

        # The LOC API does not have a dedicated endpoint for fetching metadata by identifier, so we use the search API
        url = f"{self.base_url}?fo=json&q={identifier}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            if response.status_code == 200:
                return self.parse_response(response.json(), identifier, input_type)
            else:
                raise Exception(f"API request failed with status code: {response.status_code}")
        except Exception as e:
            # Log the error and continue with the search
            # print(f"Error fetching metadata for identifier {identifier} from {self.name}: {e}")
            return None

    def parse_response(self, response, identifier, input_type):
        # Parses the response and returns a dictionary with the metadata
        lccns = []
        ocns = []
        results = response.get('results')

        if results:
            for item in results:
                # Populate ocns with 'number_oclc'
                ocns.append(self.get_ocn(item))
                # Populate lccns with 'call_number'
                lccns.append(self.get_lccn(item))

                # Check if the OCN input matches the record OCN
                if input_type == "ocn" and identifier not in ocns:
                    break
                isbns = [identifier] if input_type == 'isbn' else []

            self.catalog_data['ISBN'] = isbns
            self.catalog_data['OCN'] = str(ocns[0]) if ocns else ''
            self.catalog_data['LCCN'] = lccns
            self.catalog_data['LCCN_Source'] = ["Library of Congress"] * len(lccns)

            self.catalog_data = vd.optimize_dictionary(self.catalog_data)
            return {k.lower(): v for k, v in self.catalog_data.items()}

        return None

    def get_ocn(self, result):
        # Extracts the OCN from the result and removes hyphens
        ocn_list = result.get('number_oclc', [])
        ocn = ocn_list[0] if ocn_list else ''
        return ocn.replace('-', '')

    def get_lccn(self, result):
        # Extracts the LCCN from the result
        call_numbers = result.get('item', {}).get('call_number', [])
        lccn = next((cn for cn in call_numbers if cn != "Newspaper"), None)
        return str(lccn) if lccn is not None else ""