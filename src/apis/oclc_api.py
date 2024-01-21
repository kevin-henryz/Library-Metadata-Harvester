# apis/oclc_api.py

import requests
from .base_api import BaseAPI

class OCLCApi(BaseAPI):
    def __init__(self, client_id, client_secret):
        self.base_url = "https://classify.oclc.org/classify2/Classify?"
        self.client_id = client_id
        self.client_secret = client_secret

    def fetch_metadata(self, identifier):
        url = f"{self.base_url}isbn={identifier}&summary=true"
        response = requests.get(url)
        if response.status_code == 200:
            return self.parse_response(response.json())
        else:
            return None

    def parse_response(self, response):
        return {
            "ISBN/OCN": response.get("isbn"),
            "LCCN": response.get("lccn"),
            "LCCN_source": "OCLC",
            "DOI": response.get("doi")
        }
