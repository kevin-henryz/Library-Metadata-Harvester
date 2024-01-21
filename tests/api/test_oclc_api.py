import unittest
from unittest.mock import patch
from apis.oclc_api import OCLCApi

class TestOCLCApi(unittest.TestCase):

    @patch('apis.oclc_api.requests.get')
    def test_fetch_metadata(self, mock_get):
        # Mocking the API response
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "isbn": "1234567890",
            "lccn": "123456",
            "doi": "10.1000/xyz123"
        }

        # Initialize OCLCApi and call fetch_metadata
        api = OCLCApi(client_id='test_id', client_secret='test_secret')
        result = api.fetch_metadata("1234567890")

        # Assert that the results are as expected
        self.assertEqual(result['ISBN/OCN'], "1234567890")
        self.assertEqual(result['LCCN'], "123456")
        self.assertEqual(result['DOI'], "10.1000/xyz123")

if __name__ == '__main__':
    unittest.main()
