import re
import requests
from apis.baseAPI import BaseAPI
import util.dictionaryValidationMethod as vd


class OpenLibraryAPI(BaseAPI):
    def __init__(self):
        self.base_url = "http://openlibrary.org/api/volumes/brief/"
        self.name = "OpenLibrary"
        self.catalog_data = {
            'ISBN': [],
            'OCN': '',
            'LCCN': [],
            'LCCN_Source': []
        }

    def fetch_metadata(self, identifier, input_type):
        if input_type == "isbn":
            url = f"{self.base_url}isbn/{identifier}.json"
        elif input_type == "ocn":
            url = f"{self.base_url}oclc/{identifier}.json"
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

        if response.get('records'):
            olid = list(response['records'].keys())[0].split("/")[
                -1]  # need to get olid for header to enter the json file

        results = response['records'][f"/books/{olid}"]

        if results:
            self.catalog_data['ISBN'] = self.get_isbn(results)
            self.catalog_data['OCN'] = self.get_ocn(results)
            self.catalog_data['LCCN'] = self.get_lccn(results)
            self.catalog_data['LCCN_Source'] = ["Open Library"] * len(self.catalog_data['LCCN'])

            self.catalog_data = vd.optimize_dictionary(self.catalog_data)
            return {k.lower(): v for k, v in self.catalog_data.items()}

        return None

    def get_ocn(self, results):
        # returns ocn as string
        ocn = ''
        ocn_list = results.get('oclcs', [])
        if ocn_list:
            ocn = ocn_list[0]
        return ocn

    def get_lccn(self, results):
        # returns list of lccn
        if results.get('data'):
            lccns = results['data'].get('classifications', {}).get('lc_classifications', [])
        return lccns if lccns else []

    def get_isbn(self, results):
        # returns list of ISBN, usually includes isbn_10 and isbn_13
        isbns = results.get('isbns', [])
        return isbns if isbns else []