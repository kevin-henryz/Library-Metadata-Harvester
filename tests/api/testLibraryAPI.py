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

# Mapping of API classes to their corresponding test data files
API_TO_TEST_FILES = {
    'HarvardLibraryAPI': ('harvardlibraryapi_isbn_test.tsv', 'harvardlibraryapi_ocn_test.tsv'),
    'LibraryOfCongressAPI': ('libraryofcongressapi_isbn_test.tsv', 'libraryofcongressapi_ocn_test.tsv'),
    'GoogleBooksAPI': ('googlebooksapi_isbn_test.tsv', 'googlebooksapi_ocn_test.tsv'),
    'OpenLibraryAPI': ('openlibraryapi_isbn_test.tsv', 'openlibraryapi_ocn_test.tsv'),
    'ColumbiaLibraryAPI': ('columbialibraryapi_isbn_test.tsv', 'columbialibraryapi_ocn_test.tsv'),
    'CornellLibraryAPI': ('cornelllibraryapi_isbn_test.tsv', 'cornelllibraryapi_ocn_test.tsv'),
    'DukeLibraryAPI': ('dukelibraryapi_isbn_test.tsv', 'dukelibraryapi_ocn_test.tsv'),
    'IndianaLibraryAPI': ('indianalibraryapi_isbn_test.tsv', 'indianalibraryapi_ocn_test.tsv'),
    'JohnsHopkinsLibraryAPI': ('johnshopkinslibraryapi_isbn_test.tsv', 'johnshopkinslibraryapi_ocn_test.tsv'),
    'NorthCarolinaStateLibraryAPI': ('northcarolinastatelibraryapi_isbn_test.tsv', 'northcarolinastatelibraryapi_ocn_test.tsv'),
    'PennStateLibraryAPI': ('pennstatelibraryapi_isbn_test.tsv', 'pennstatelibraryapi_ocn_test.tsv'),
    'YaleLibraryAPI': ('yalelibraryapi_isbn_test.tsv', 'yalelibraryapi_ocn_test.tsv'),
    'StanfordLibraryAPI': ('stanfordlibraryapi_isbn_test.tsv', 'stanfordlibraryapi_ocn_test.tsv')
}

class TestLibraryAPIs(unittest.TestCase):

    def setUp(self):
        """Set up test environment before each test."""
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_file_dir)
        self.data_dir = os.path.join(parent_dir, 'data', 'tsv')

    def test_apis_with_isbn(self):
        """Test each API with ISBN identifiers."""
        for api_name, (isbn_file, _) in API_TO_TEST_FILES.items():
            with self.subTest(api=api_name):
                api_class = globals()[api_name]()  # Instantiate the API class
                test_file = os.path.join(self.data_dir, isbn_file)
                with open(test_file, 'r') as f:
                    reader = csv.DictReader(f, delimiter='\t')
                    for row in reader:
                        identifier = row['ISBN']
                        result = api_class.fetch_metadata(identifier, 'isbn')
                        self.assertIsNotNone(result, f"Result should not be None for ISBN {identifier}")
                        for key, value in row.items():
                            if key.lower() == 'ocn': 
                                self.assertEqual(result[key.lower()], value, f"{value} should match the result for {key} of ISBN {identifier}")
                                continue
                            self.assertIn(value, result[key.lower()], f"{value} should be in the result for {key} of ISBN {identifier}")

    def test_apis_with_ocn(self):
        """Test each API with OCN identifiers."""
        for api_name, (_, ocn_file) in API_TO_TEST_FILES.items():
            with self.subTest(api=api_name):
                api_class = globals()[api_name]() 
                test_file = os.path.join(self.data_dir, ocn_file)
                with open(test_file, 'r') as f:
                    reader = csv.DictReader(f, delimiter='\t')
                    for row in reader:
                        identifier = row['OCN'] 
                        result = api_class.fetch_metadata(identifier, 'ocn')
                        self.assertIsNotNone(result, f"Result should not be None for OCN {identifier}")
                        for key, value in row.items():
                            if key.lower() == 'ocn':  
                                self.assertEqual(result[key.lower()], value, f"{value} should match the result for {key} of OCN {identifier}")
                                continue
                            self.assertIn(value, result[key.lower()], f"{value} should be in the result for {key} of OCN {identifier}")

if __name__ == '__main__':
    unittest.main()