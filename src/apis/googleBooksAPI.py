import requests
from .baseAPI import BaseAPI
import re
from ratelimit import limits, sleep_and_retry

class GoogleBooksAPI(BaseAPI):
    def __init__(self):
        self.base_url = "https://www.googleapis.com/books/v1/volumes?q="
        self.name = "GoogleBooks"

    @sleep_and_retry
    @limits(calls=1, period=1)  # Allow 1 request per second
    def fetch_metadata(self, identifier, input_type):
        url = f"{self.base_url}{input_type}:{identifier}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check for HTTP request errors
            return self.parse_response(response.json(), identifier, input_type)
        except Exception as e:
            #print(f"Error fetching metadata for identifier {identifier} from {self.name}: {e}")
            return None
    def parse_response(self, response, identifier, input_type):
        items = response.get('items')
        if items:
            volume_info = items[0].get('volumeInfo', {})
            industry_identifiers = volume_info.get('industryIdentifiers', [])

            # Extract ISBNs, OCNs, and LCCNs in a similar structured manner as HarvardAPI
            isbn = self.get_identifiers(industry_identifiers, ['ISBN_13', 'ISBN_10'], True)
            ocn = self.clean_identifier(identifier if input_type == "oclc" else self.get_identifier(industry_identifiers, 'OCLC'))
            lccn = self.get_identifiers(industry_identifiers, ['LCCN'])

            # Compile the results into a dictionary
            result = {
                'isbn': isbn,
                'ocn': ocn,
                'lccn': lccn,
                'lccn_source': ["Google Books"] * len(lccn)
            }

            return result
        return None

    def get_identifiers(self, results, types, remove_hyphens=False):
        """Extract and return identifiers based on type."""
        identifiers = []
        for item in results:
            if item.get('type') in types:
                identifier = item.get('identifier', '')
                if remove_hyphens:
                    identifier = re.sub(r'-', '', identifier)  # Remove hyphens
                identifiers.append(identifier)
        return identifiers

    def get_identifier(self, results, type):
        """Get a single identifier of a specified type."""
        for item in results:
            if item.get('type') == type:
                return re.sub(r'-', '', item.get('identifier', ''))
        return ''
    
    def clean_identifier(self, identifier):
        """Removes hyphens and unnecessary characters from identifiers like OCN or LCCN."""
        return re.sub(r'[- ]', '', identifier) if identifier else ''