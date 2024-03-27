import os

import pytest
from itertools import product
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
TOTAL_TESTS = len(API_CLASSES) * 2
TEST_COMBINATIONS = list(product([api.__name__ for api in API_CLASSES], ['isbn', 'ocn']))


@pytest.fixture(scope='class')
def data_dir():
    current_dir = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(current_dir, '..', 'data', 'tsv'))

@pytest.mark.parametrize("ApiClass", API_CLASSES, ids=[api.__name__ for api in API_CLASSES])
@pytest.mark.parametrize("file_suffix", ['isbn', 'ocn'])
class TestLibraryAPIs:
    current_test_number = 0
    def test_api_responses(self, ApiClass, file_suffix, data_dir):
        """Test APIs with ISBN and OCN identifiers."""

        TestLibraryAPIs.current_test_number += 1
        print(f"Running test {TestLibraryAPIs.current_test_number}/{TOTAL_TESTS}: {ApiClass.__name__}, {file_suffix}")

        api_instance = ApiClass()  # Initialize API class once per API
        api_name = api_instance.__class__.__name__.lower()
        
        test_file = os.path.join(data_dir, f"{api_name}_{file_suffix}_test.tsv")
        if not os.path.exists(test_file):
            pytest.skip(f"Test file {test_file} does not exist")    
        with open(test_file, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            
            for row in reader:
                identifier = row[file_suffix.upper()]
                #print(identifier)
                #continue
                # If identifier is None, consider the test passed for this row
                if not identifier:
                    continue  # Skip this row if the identifier is missing or None
                result = api_instance.fetch_metadata(identifier, file_suffix)

                if result is None:
                    other_fields = ['isbn', 'ocn', 'lccn', 'lccn_source']
                    other_fields.remove(file_suffix)  # Remove the current suffix being tested
                    # Check if all other fields except the current one are empty
                    if all(not row.get(field.upper(), '').strip(" \t") for field in other_fields):
                        continue  # If only the current field is non-empty, skip this entry
                    else:
                        assert False, f"API {api_name} returned None for {file_suffix.upper()} {identifier} when other data fields are present"

                # Validate all expected fields against the result
                for field in ['isbn', 'ocn', 'lccn', 'lccn_source']:
                    expected_values = row[field.upper()].strip(" \t").split(';') if row[field.upper()] else []
                    if field == 'ocn':  # 'ocn' is expected to be a single string
                        assert result.get(field, '') == row[field.upper()].strip(), f"{field.upper()} does not match for {api_name} and identifier {identifier}"
                    else:  # All other fields are expected to be lists
                        assert result.get(field, []) == expected_values, f"{field.upper()} does not match for {api_name} and identifier {identifier}"

