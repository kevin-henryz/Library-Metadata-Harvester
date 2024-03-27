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

import time

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

import time

def search_results(api_class, input_type):
    total_time = 0

    # Initialize an instance of the API class
    api_instance = api_class()

    output_file = f"../data/output/{api_instance.name}_{input_type}_output.txt"

    with open(f'../data/input/{api_instance.name}_{input_type}_test.txt', 'r') as f_in, open(output_file, 'w') as f_out:

        for line in f_in:
            line = line.strip()
            start_time = time.time()

            metadata = api_instance.fetch_metadata(line, input_type)
            if metadata:
                f_out.write(f"{metadata}\n")
            end_time = time.time()
            elapsed_time = end_time - start_time
            total_time += elapsed_time

        f_out.write(f"Total time for {input_type} inputs: {total_time} seconds")

    return total_time

def run_apis(apis, inputs):
    total_time_isbn = 0
    total_time_ocn = 0

    for api_class in apis:
        for input_type in inputs:
            total_time = search_results(api_class, input_type)
            if input_type == 'isbn':
                total_time_isbn += total_time
            elif input_type == 'ocn':
                total_time_ocn += total_time

    print(f"Total time for all ISBN inputs: {total_time_isbn} seconds")
    print(f"Total time for all OCN inputs: {total_time_ocn} seconds")

if __name__ == "__main__":
    # run individual api and input type
    apis = [
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
    inputs = ['isbn', 'ocn']

    run_apis(apis, inputs)

