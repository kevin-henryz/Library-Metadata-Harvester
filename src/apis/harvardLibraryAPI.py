import re
import requests
from ratelimit import limits, sleep_and_retry
import util.dictionaryValidationMethod as vd
from apis.baseAPI import BaseAPI



class HarvardLibraryAPI(BaseAPI):
    def __init__(self):
        self.base_url = "https://api.lib.harvard.edu/v2/items"
        self.name = "Harvard"
        self.catalog_data = {
            'ISBN': [],
            'OCN': '',
            'LCCN': [],
            'LCCN_Source': []
        }

    @sleep_and_retry
    @limits(calls=1, period=1)  # Allow 1 request per second
    def fetch_metadata(self, identifier, input_type):

        url = f"{self.base_url}.json?identifier={identifier}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors (status code >= 400)
            if response.status_code == 200:
                return self.parse_response(response.json(), identifier, input_type)
            else:
                raise Exception(f"API request failed with status code: {response.status_code}")
        except Exception as e:
            # Log the error and continue with the search
            # print(f"Error fetching metadata for identifier {identifier} from {self.name}: {e}")
            return None

    def parse_response(self, response, identifier, input_type):
        if response.get('items'):
            mods = response.get('items', {}).get('mods', {})

            if isinstance(mods, list):
                results = mods[0]
            elif isinstance(mods, dict):
                results = mods

            if results:
                self.catalog_data['ISBN'] = self.get_isbn(results.get('identifier', []))
                self.catalog_data['OCN'] = self.get_ocn(results.get('identifier', ''))
                self.catalog_data['LCCN'] = self.get_lccn(results.get('classification', []))
                self.catalog_data['LCCN_Source'] = ["Harvard"] * len(self.catalog_data['LCCN'])

            if input_type == "ocn":
                if identifier != self.catalog_data['OCN']:
                    return None

            self.catalog_data = vd.optimize_dictionary(self.catalog_data)
            return {k.lower(): v for k, v in self.catalog_data.items()}

        return None

    def get_lccn(self, results):

        lccns = []
        if isinstance(results, list):
            for item in results:
                if item.get('@authority') == 'lcc':
                    lccns.append(item.get('#text', ''))
        elif isinstance(results, dict) and results.get('@authority') == 'lcc':
            lccns.append(results.get('#text', ''))
        return lccns

    def get_ocn(self, results):
        # Returns the first OCN found in the response, with hyphens removed
        for item in results:
            if isinstance(item, dict) and item.get('@type') == 'oclc':
                ocn = item.get('#text', '')
                return re.sub(r'-', '', ocn)  # Remove hyphens
        return ''

    def get_isbn(self, results):
        # Returns a list of ISBNs, which were stored in the 'identifier' field in the response, with hyphens removed
        isbns = []
        for item in results:
            if isinstance(item, dict) and item.get('@type') == 'isbn' and item.get('@invalid') != 'yes':
                isbn = item.get('#text', "").split()[0]  # Take first part if there are spaces
                isbns.append(re.sub(r'-', '', isbn))  # Remove hyphens
        return isbns