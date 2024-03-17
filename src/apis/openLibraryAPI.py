# apis/openLibrary_api.py
import re
import requests
from .baseAPI import BaseAPI



class OpenLibraryAPI(BaseAPI):
    def __init__(self):
        self.base_url = "https://openlibrary.org/"
        self.name = "OpenLibrary"

    def fetch_metadata(self, identifier, input_type):
        if input_type != "isbn": # OpenLibrary does not support searching by OCN
            #print(f"{self.name} API does not support {input_type} input")
            return None
        url = f"{self.base_url}isbn/{identifier}.json"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors (status code >= 400)
            if response.status_code == 200:
                return self.parse_response(response.json(), identifier, input_type)
            else:
                raise Exception(f"API request failed with status code: {response.status_code}")
        except Exception as e:
            # Log the error and continue with the search
            #print(f"Error fetching metadata for identifier {identifier} from {self.name}: {e}")
            return None

    # if present and requested, returns ISBN_13, single OCN, and single LCCN with source from the response
    def parse_response(self, response, identifier, input_type):
        return {
            "isbn": self.get_isbn(response),
            "ocn": self.get_ocn(response),
            "lccn": self.get_lccn(response),
            "lccn_source": ["Open Library"]* len(self.get_lccn(response))
        }

    def get_ocn(self, response):
        result = response.get("oclc")
        if result is not None:  
            if not isinstance(result, list):  
                result = [result] 
        else:
            result = [] 
        return result

    def get_lccn(self, response):
        result = response.get("lccn")
        if result is not None: 
            if not isinstance(result, list):  
                result = [result] 
        else:
            result = []
        return result

    def get_isbn(self, response):

            isbns = []
            result = response.get("isbn_13")
            result2 = response.get("isbn_10")
            if result is not None: 
                if not isinstance(result, list): 
                    result = [result] 
                isbns.extend(result)
            if result2 is not None: 
                if not isinstance(result2, list):
                    result2 = [result2]
                isbns.extend(result2)
            return isbns
