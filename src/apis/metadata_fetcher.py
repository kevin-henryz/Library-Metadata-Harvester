from apis.oclc_api import OCLCApi
# from apis.other_api import OtherApiClass

class MetadataFetcher:
    def __init__(self):
        self.apis = [
            OCLCApi(client_id='...', client_secret='...'),
            # Initialize other API classes here
        ]

    def fetch_metadata(self, identifier):
        for api in self.apis:
            metadata = api.fetch_metadata(identifier)
            if metadata:
                return metadata
        return None
