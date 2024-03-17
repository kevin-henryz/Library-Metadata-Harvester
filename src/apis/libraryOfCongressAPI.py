import requests
import re
from ratelimit import limits, sleep_and_retry
from .baseAPI import BaseAPI

# The LOC API does not have a dedicated endpoint for fetching metadata by identifier, so we use the search API
# The input must be ISBN, as OCN input doesn't return correct results
class LibraryOfCongressAPI(BaseAPI):
    def __init__(self):
        self.base_url = "https://www.loc.gov/search/"
        self.name = "LOC"

    @sleep_and_retry
    @limits(calls=10, period=10)  # Allow 10 requests every 10 seconds for burst limit
    def fetch_metadata(self, identifier, input_type):
        if input_type != "isbn":
            print(f"{self.name} API does not support {input_type} input")
            return None

        # The LOC API does not have a dedicated endpoint for fetching metadata by identifier, so we use the search API
        url = f"{self.base_url}?fo=json&q={identifier}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return self.parse_response(response.json(), identifier, input_type)
        except Exception as e:
            print(f"Error fetching metadata for identifier {identifier} from {self.name}: {e}")
        return None

    def parse_response(self, response, identifier, input_type):
        # parses the response and returns a tab delimited string with the metadata
        results = response.get('results')
        if results:
            first_result = results[0]

            isbn = [identifier] if identifier != None else [] 
            ocn = self.get_ocn(first_result)
            lccn = [self.get_lccn(first_result)] if self.get_lccn(first_result) != None else []

            source = "LOC"
            return {
                'isbn': isbn,
                'ocn': ocn,
                'lccn': lccn,
                'lccn_source': ["Library of Congress"] * len(lccn),
            }
        return None

    def get_ocn(self, result):
        # Extract the first OCN if available and remove any hyphens from it
        ocn_list = result.get('number_oclc', '')
        ocn = ocn_list[0] if isinstance(ocn_list, list) and ocn_list else ''
        ocn_cleaned = ocn.replace('-', '')  # Remove hyphens
        return ocn_cleaned

    def get_lccn(self, result):
        call_numbers = result.get('item', {}).get('call_number', [])
        # If "Newspaper" is present, return the next call number if it is a newspaper, the string "newspaper" appears
        # as the first item in the call number list for some reason.
        if "Newspaper" in call_numbers:
            index = call_numbers.index("Newspaper")
            if index + 1 < len(call_numbers):
                return call_numbers[index + 1]
            else:
                return   # If "Newspaper" is the only call number
        elif call_numbers:
            return call_numbers[0]
        else:
            return 