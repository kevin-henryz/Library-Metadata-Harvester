import requests

class BaseScraping:
    def fetch_metadata(self, identifier, input_type):
        raise NotImplementedError
    
    def is_online(self, url='http://www.google.com/', timeout=5):
        """Check if the internet connection is available."""
        try:
            requests.get(url, timeout=timeout)
            return True
        except (requests.ConnectionError, requests.Timeout):
            return False