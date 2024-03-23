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

def search_results(source, input_type, name=None):
    total_time = 0
    if isinstance(source, tuple):
        api, identifier = source
        output_file = f"{api.name}API_{input_type}_output.txt"
    else:
        webscraper = source
        output_file = f"{name}API_{input_type}_output.txt"

    with open(f'../data/{input_type}-test.txt', 'r') as f_in, open(output_file, 'w') as f_out:

        for line in f_in:
            line = line.strip()
            start_time = time.time()
            if isinstance(source, tuple):
                metadata = api.fetch_metadata(line, identifier)
            else:
                metadata = webscraper.fetch_metadata(line, input_type)
            if metadata:
                f_out.write(f"{metadata}\n")
            end_time = time.time()
            elapsed_time = end_time - start_time
            total_time += elapsed_time

        f_out.write(f"Total time for {input_type} inputs: {total_time} seconds")

    return total_time

def run_apis():
    apis = [
        HarvardLibraryAPI(),
        LibraryOfCongressAPI(),
        GoogleBooksAPI(),
        OpenLibraryAPI()
    ]
    inputs = ['isbn', 'ocn']
    total_time_isbn = 0
    total_time_ocn = 0
    for api in apis:
        for input_type in inputs:
            total_time = search_results((api, input_type), input_type)
            if input_type == 'isbn':
                total_time_isbn += total_time
            elif input_type == 'ocn':
                total_time_ocn += total_time

    print(f"Total time for all ISBN inputs: {total_time_isbn} seconds")
    print(f"Total time for all OCN inputs: {total_time_ocn} seconds")

def run_individual_api(api, input_type):
    total_time = search_results((api, input_type), input_type)
    print(f"Total time for {input_type} inputs: {total_time} seconds")

def run_webscrapers():
    webscrapers = [
        ColumbiaLibraryAPI(),
        CornellLibraryAPI(),
        DukeLibraryAPI(),
        IndianaLibraryAPI(),
        JohnsHopkinsLibraryAPI(),
        NorthCarolinaStateLibraryAPI(),
        PennStateLibraryAPI(),
        YaleLibraryAPI(),
        StanfordLibraryAPI()
    ]
    names = ['Columbia', 'Cornell', 'Duke', 'Indiana', 'JHU', 'NCSU', 'PennState', 'Yale', 'Stanford']
    inputs = ['isbn', 'ocn']
    total_time_isbn = 0
    total_time_ocn = 0

    for webscraper, name in zip(webscrapers, names):
        for input_type in inputs:
            total_time = search_results(webscraper, input_type, name)
            if input_type == 'isbn':
                total_time_isbn += total_time
            elif input_type == 'ocn':
                total_time_ocn += total_time

    print(f"Total time for all ISBN inputs: {total_time_isbn} seconds")
    print(f"Total time for all OCN inputs: {total_time_ocn} seconds")

def run_individual_webscraper(webscraper, input_type, name):
    total_time = search_results(webscraper, input_type, name)
    print(f"Total time for {input_type} inputs: {total_time} seconds")

if __name__ == "__main__":

    run_apis() # run all apis, all input types

    # run_webscrapers() # run all webscrapers, all input types

    # run individual api and input type
    # api = HarvardLibraryAPI()  # HarvardLibraryAPI(), LibraryOfCongressAPI(), GoogleBooksAPI(), OpenLibraryAPI()
    # input_type = 'isbn'  # 'isbn' or 'ocn
    # run_individual_api(api, input_type)

    #run individual webscraper and input
    # webscraper = JohnsHopkinsLibraryAPI()  # ColumbiaLibraryAPI(), CornellLibraryAPI(), DukeLibraryAPI(),
    # name = 'JHU'  # 'Columbia', 'Cornell', 'Duke', 'Indiana', 'JHU', 'NCSU', 'PennState', 'Yale', 'Stanford'
    # input_type = 'isbn'  # 'isbn' or 'ocn'
    # run_individual_webscraper(webscraper, input_type
