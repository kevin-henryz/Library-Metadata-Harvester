class BaseAPI:
    def fetch_metadata(self, identifier, input_type):
        raise NotImplementedError

    def parse_response(self, response, identifier, input_type):
        raise NotImplementedError
