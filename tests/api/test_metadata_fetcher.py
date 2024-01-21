import unittest
from unittest.mock import patch
from apis.metadata_fetcher import MetadataFetcher

class TestMetadataFetcher(unittest.TestCase):

    @patch('metadata_fetcher.OCLCApi.fetch_metadata')
    def test_fetch_metadata(self, mock_fetch_metadata):
        # Mocking the metadata fetch
        mock_fetch_metadata.return_value = {
            "ISBN/OCN": "1234567890",
            "LCCN": "123456",
            "LCCN_source": "OCLC",
            "DOI": "10.1000/xyz123"
        }

        # Initialize MetadataFetcher and call fetch_metadata
        fetcher = MetadataFetcher()
        result = fetcher.fetch_metadata("1234567890")

        # Assert that the results are as expected
        self.assertEqual(result['ISBN/OCN'], "1234567890")
        self.assertEqual(result['LCCN'], "123456")
        self.assertEqual(result['DOI'], "10.1000/xyz123")

if __name__ == '__main__':
    unittest.main()
