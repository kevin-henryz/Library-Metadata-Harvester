class BaseAPI:
    def fetch_metadata(self, identifier):
        raise NotImplementedError

    def parse_response(self, response):
        raise NotImplementedError
