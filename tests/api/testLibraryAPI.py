import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import unittest
# API modules for gathering library metadata from various sources
from src.apis.harvardLibraryAPI import HarvardLibraryAPI
from src.apis.libraryOfCongressAPI import LibraryOfCongressAPI
from src.apis.googleBooksAPI import GoogleBooksAPI
from src.apis.openLibraryAPI import OpenLibraryAPI

# Web scraping modules for extracting data from various university libraries
from src.webScraping.columbiaLibraryAPI import ColumbiaLibraryAPI
from src.webScraping.cornellLibraryAPI import CornellLibraryAPI
from src.webScraping.dukeLibraryAPI import DukeLibraryAPI
from src.webScraping.indianaLibraryAPI import IndianaLibraryAPI
from src.webScraping.johnsHopkinsLibraryAPI import JohnsHopkinsLibraryAPI
from src.webScraping.northCarolinaStateLibraryAPI import NorthCarolinaStateLibraryAPI
from src.webScraping.pennStateLibraryAPI import PennStateLibraryAPI
from src.webScraping.yaleLibraryAPI import YaleLibraryAPI
from src.webScraping.stanfordLibraryAPI import StanfordLibraryAPI
import csv

API_CLASSES = [
    HarvardLibraryAPI,
    LibraryOfCongressAPI,
    GoogleBooksAPI,
    OpenLibraryAPI,
    ColumbiaLibraryAPI,
    CornellLibraryAPI,
    DukeLibraryAPI,
    IndianaLibraryAPI,
    JohnsHopkinsLibraryAPI,
    NorthCarolinaStateLibraryAPI,
    PennStateLibraryAPI,
    YaleLibraryAPI,
    StanfordLibraryAPI
]


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR,'data', 'tsv')


class TestLibraryAPIs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up environment before any tests run."""
        current_dir = os.path.dirname(__file__)  # Directory where this script is located
        cls.data_dir = os.path.abspath(os.path.join(current_dir, '..', 'data', 'tsv'))  # Adjust according to your structure

    def test_api_responses(self):
        """Test APIs with ISBN and OCN identifiers."""
        for ApiClass in API_CLASSES:
            api_instance = ApiClass()  # Initialize API class once per API
            api_name = api_instance.__class__.__name__.lower()
            for file_suffix in ['isbn', 'ocn']:  # Loop over both types of identifiers
                test_file = os.path.join(self.data_dir, f"{api_name}_{file_suffix}_test.tsv")
                if not os.path.exists(test_file):
                    self.skipTest(f"Test file {test_file} does not exist")    
                with open(test_file, 'r') as f, self.subTest(api=api_name, file=test_file):
                    reader = csv.DictReader(f, delimiter='\t')
                    for row in reader:
                        identifier = row[file_suffix.upper()]
                        #print(identifier)
                        #continue
                        # If identifier is None, consider the test passed for this row
                        if not identifier:
                            continue  # Skip this row if the identifier is missing or None
                        result = api_instance.fetch_metadata(identifier, file_suffix)
                        # Check the API response
                        self.assertIsNotNone(result, f"API {api_name} returned None for {file_suffix.upper()} {identifier}")
                        # Validate all expected fields against the result
                        for field in ['isbn', 'ocn', 'lccn', 'lccn_source']:
                            expected_values = row[field.upper()].strip().split() if row[field.upper()] else []
                            if field == 'ocn':  # 'ocn' is expected to be a single string
                                self.assertEqual(result.get(field, ''), row[field.upper()].strip(), f"{field.upper()} does not match for {api_name} and identifier {identifier}")
                            else:  # All other fields are expected to be lists
                                self.assertEqual(result.get(field, []), expected_values, f"{field.upper()} does not match for {api_name} and identifier {identifier}")

if __name__ == '__main__':
    unittest.main(verbosity=2)