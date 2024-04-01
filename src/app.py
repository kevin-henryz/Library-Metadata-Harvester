import os
import platform
from pathlib import Path
import sys
import logging
import threading
import time
import csv
import webbrowser
import subprocess
import queue
from selenium.common.exceptions import WebDriverException
import json



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))


import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from tkinter.filedialog import asksaveasfile

# Importing custom modules for processing files and handling GUI elements
from util.fileProcessor import verifyFileFormat
from gui.priorityList import PriorityList

# Database management imports for application data handling
from db.databaseManager import DatabaseManager

# API modules for gathering library metadata from various sources
from apis.harvardLibraryAPI import HarvardLibraryAPI
from apis.libraryOfCongressAPI import LibraryOfCongressAPI
from apis.googleBooksAPI import GoogleBooksAPI
from apis.openLibraryAPI import OpenLibraryAPI

# Web scraping modules for extracting data from various university libraries
from webScraping.columbiaLibraryAPI import ColumbiaLibraryAPI
from webScraping.cornellLibraryAPI import CornellLibraryAPI
from webScraping.dukeLibraryAPI import DukeLibraryAPI
from webScraping.indianaLibraryAPI import IndianaLibraryAPI
from webScraping.johnsHopkinsLibraryAPI import JohnsHopkinsLibraryAPI
from webScraping.northCarolinaStateLibraryAPI import NorthCarolinaStateLibraryAPI
from webScraping.pennStateLibraryAPI import PennStateLibraryAPI
from webScraping.yaleLibraryAPI import YaleLibraryAPI
from webScraping.stanfordLibraryAPI import StanfordLibraryAPI

class LibraryMetadataHarvesterApp(tk.Tk):
    """A GUI application for harvesting library metadata from different sources.

    Attributes:
        source_mapping (dict): An initially empty mapping that will be populated with library names as keys and their respective API class instances as values.
        source_threads (dict): A dictionary holding threading objects corresponding to the initialization of each API class. This allows for asynchronous initialization and tracking of each API's loading status.
        db_manager (DatabaseManager): An object that handles interactions with the application's database for storing and retrieving metadata.
        priority_list (list): An ordered list of library names representing the user's preference order for metadata source selection.
        search_status_var (tk.StringVar): A tkinter StringVar used to track and display the status of ongoing metadata searches within the GUI.
        search_active (bool): A boolean flag indicating whether a metadata search is currently in progress.
        total_identifiers (int): The total number of unique identifiers (e.g., ISBNs) to be searched in the metadata harvesting process.
        current_identifier (int): The index of the current identifier being searched in the list of total identifiers.
        
    """
    
    def __init__(self):
        """Initialize the application, its variables, and UI components."""
        super().__init__()
        self.app_data_dir = self.get_app_data_directory()
        self.output_file_path = None
        self.log_window_open = False 
        self.last_processed = None
        self.log_file_last_size = 0
        self.source_mapping = {}
        self.priority_list = [
        'Google Books (API)', 'Harvard Library (API)',
        'Library of Congress (API)', 'Open Library (API)',
        'Columbia Library (Blacklight)', 'Cornell Library (Blacklight)',
        'Duke Library (Blacklight)', 'Indiana Library (Blacklight)',
        'Johns Hopkins Library (Blacklight)', 'North Carolina State Library (Blacklight)',
        'Pennsylvania State Library (Blacklight)', 'Stanford Library (Blacklight)',
        'Yale Library (Blacklight)'
    ]
        self.setup_logging()
        self.configure_app()
        self.initialize_database()
        self.setup_ui()
        self.initialize_sources()
                
        self.unused_sources = []
        self.load_source_lists()
        self.search_status_var = tk.StringVar(self)
        self.search_status_label = tk.Label(self, textvariable=self.search_status_var, font=("Helvetica", 16), bg='#202020', fg='white')
        self.search_active = False
        self.total_identifiers = 0
        self.current_identifier = 0
        self.search_start_time = None
        self.search_total_time = None


    def get_app_data_directory(self):
        """Get the path to the application's data directory."""
        if platform.system() == "Windows":
            app_data_path = Path(os.getenv('APPDATA')) / 'LibraryMetadataHarvester'
        elif platform.system() == "Darwin":
            app_data_path = Path.home() / 'Library' / 'Application Support' / 'LibraryMetadataHarvester'
        else:  # Linux and other Unix-like OSes
            app_data_path = Path.home() / '.LibraryMetadataHarvester'

        app_data_path.mkdir(parents=True, exist_ok=True)
        return app_data_path

    def configure_app(self):
        """Configure the main window settings and styles."""
        self.title('Library Metadata Harvester')
        self.configure(bg='#202020') 
        
        # Get and store the screen width and height
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        
        # Calculate and store width and height as a percentage of the screen size
        self.app_width = int(self.screen_width * 0.55) 
        self.app_height = int(self.screen_height * 0.4)

        # Calculate and store the position to center the window on the screen
        self.app_x = (self.screen_width // 2) - (self.app_width // 2)
        self.app_y = (self.screen_height // 2) - (self.app_height // 2)
        
        # Set the geometry of the window
        self.geometry('{}x{}+{}+{}'.format(self.app_width, self.app_height, self.app_x, self.app_y))
        
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TButton', background='#404040', foreground='white', borderwidth=1)
        self.style.configure('TFrame', background='#202020')
        self.style.configure('TCheckbutton', background='#202020', foreground='white')
        self.style.configure('TRadioButton', background='#202020', foreground='white')
        self.style.configure('TLabel', background='#202020', foreground='white')
        self.style.configure('TEntry', background='#404040', foreground='white', fieldbackground='#404040', borderwidth=1)
        self.style.map('TEntry', fieldbackground=[('focus', '#404040')], foreground=[('focus', 'white')])
        self.style.map('TButton',
               background=[('active', '#606060')],
               foreground=[('active', 'black')])
        self.style.map('TCheckbutton',
               background=[('active', '#404040')],
               foreground=[('active', 'white')],
               selectColor=[('active', '#202020')])
        self.style.map('TRadioButton',
               background=[('active', '#404040')],
               foreground=[('active', 'white')])

    def setup_logging(self):
        """Setup application logging."""
        self.log_file_path = self.app_data_dir / 'example.log'
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            handlers=[
                                logging.FileHandler(self.log_file_path),
                                logging.StreamHandler()
                            ])
        logging.info("Application started")
       

    def initialize_database(self):
        """Initialize the application's database and required tables."""
        db_path = self.get_app_data_directory()
        self.db_manager = DatabaseManager(db_path=db_path)
        self.db_manager.create_table("books", "Isbn TEXT PRIMARY KEY, Ocn TEXT")
        self.db_manager.create_table("lccn", "Lccn_id INTEGER PRIMARY KEY AUTOINCREMENT, Lccn TEXT, Source TEXT")
        self.db_manager.create_table("book_lccn", "Isbn TEXT, Lccn_id INTEGER, FOREIGN KEY (Isbn) REFERENCES books (Isbn), FOREIGN KEY (Lccn_id) REFERENCES lccn (Lccn_id)")

    def setup_ui(self):
        """Setup the user interface for the application."""
        self.setup_top_frame()
        self.setup_input_frame()
        self.setup_output_options()
        self.setup_buttons_frame()
        self.search_in_progress = False
        self.search_status_var = tk.StringVar(value="")
        self.search_status_label = tk.Label(self, textvariable=self.search_status_var, font=("Helvetica", 16), bg='#202020', fg='white')
        self.search_status_label.pack_forget()  # Initially hide it


    def setup_top_frame(self):
        """Setup the top frame UI containing input and output options."""
        self.top_frame = ttk.Frame(self, style='TFrame')
        self.top_frame.pack(side='top', fill='x', padx=5, pady=5)


    def setup_input_frame(self):
        """Setup the frame for input options."""
        self.input_frame = ttk.Frame(self.top_frame, style='TFrame')
        self.input_frame.pack(side='left', fill='x', expand=True, padx=(0, 5)) 
        self.configure_input_frame_contents()

    def configure_input_frame_contents(self):
        """Configure the contents and layout of the input frame."""
        ttk.Label(self.input_frame, text="Data Type of Input File:",style='TLabel').grid(row=0, column=0, sticky='w')
        self.input_file_type = tk.IntVar(value=1)  # Default to ISBN
        ttk.Radiobutton(self.input_frame, text="ISBN", variable=self.input_file_type, value=1, style='TRadiobutton',command=self.update_checkbox_state).grid(row=2, column=0, sticky='w')
        ttk.Radiobutton(self.input_frame, text="OCN", variable=self.input_file_type, value=0, style='TRadiobutton',command=self.update_checkbox_state).grid(row=2, column=1, sticky='w')

        ttk.Label(self.input_frame, text="Browse Input File:", style='TLabel').grid(row=3, column=0, sticky='w', pady=(10, 0))
        self.file_entry = ttk.Entry(self.input_frame, width=40)
        self.file_entry.grid(row=4, column=0, sticky='w')
        ttk.Button(self.input_frame, text="Browse", command=self.browse_file).grid(row=4, column=1, padx=5)

    def update_checkbox_state(self):
        """Update the state of checkboxes based on the input file type selection."""
        if self.input_file_type.get() == 1:  # ISBN selected
            self.output_value_isbn.set(True)
            self.output_value_ocn.set(False)
            self.isbn_checkbutton['state'] = 'disabled'  
            self.ocn_checkbutton['state'] = 'normal'
        else:  # OCN selected
            self.output_value_ocn.set(True)
            self.output_value_isbn.set(False)
            self.ocn_checkbutton['state'] = 'disabled'
            self.isbn_checkbutton['state'] = 'normal'

    def setup_buttons_frame(self):
        """Setup the frame for control buttons."""
        self.button_frame = ttk.Frame(self, style='TFrame')
        self.button_frame.pack(fill='x', padx=5, pady=10)
        self.configure_buttons()

    def configure_buttons(self):
        """Configure the buttons and their actions in the buttons frame."""
        self.choose_output_file_button = ttk.Button(self.button_frame, text="Choose Output File", command=self.choose_output_file)
        self.choose_output_file_button.pack(side='left', padx=5)        
        
        self.set_priority_button = ttk.Button(self.button_frame, text="Set Searching Priority", command=self.set_priority)
        self.set_priority_button.pack(side='left', padx=5)

        self.start_button = ttk.Button(self.button_frame, text="Start Search", command=self.start_search)
        self.start_button.pack(side='left', padx=5)

        self.open_output_file_button = ttk.Button(self.button_frame, text="Open Output File", command=self.open_output_file)
        self.open_output_file_button.pack(side='left', padx=5)

        self.open_log_button = ttk.Button(self.button_frame, text="Open Log", command=self.open_log)
        self.open_log_button.pack(side='left', padx=5)

        self.clear_log_button = ttk.Button(self.button_frame, text="Clear Log", command=self.clear_log)
        self.clear_log_button.pack(side='left', padx=5)

        self.stop_button = ttk.Button(self.button_frame, text="Stop Search", command=lambda: self.finalize_search(manually_stopped=True), state='disabled')



   
    def setup_output_options(self):
        """Setup the frame for output options."""
        self.output_frame = ttk.Frame(self.top_frame, style='TFrame')
        self.output_frame.pack(side='left', fill='x', expand=True, padx=(0, 0))
        self.configure_output_options()

    def configure_output_options(self):
        """Configure the output options checkboxes."""
        ttk.Label(self.output_frame, text="Output Options:", style='TLabel').pack(anchor='w')
        self.output_value_isbn = tk.BooleanVar()
        self.output_value_ocn = tk.BooleanVar()
        self.output_value_lccn = tk.BooleanVar()
        self.output_value_lccn_source = tk.BooleanVar()
        self.isbn_checkbutton = ttk.Checkbutton(self.output_frame, text="ISBN", variable=self.output_value_isbn, style='TCheckbutton')
        self.isbn_checkbutton.pack(anchor='w', padx=5, pady=2)
        self.isbn_checkbutton['state'] = 'disabled' 
        self.output_value_isbn.set(True) 
        self.ocn_checkbutton = ttk.Checkbutton(self.output_frame, text="OCN", variable=self.output_value_ocn, style='TCheckbutton')
        self.ocn_checkbutton.pack(anchor='w', padx=5, pady=2)
        ttk.Checkbutton(self.output_frame, text="LCCN", variable=self.output_value_lccn, style='TCheckbutton').pack(anchor='w', padx=5, pady=2)
        ttk.Checkbutton(self.output_frame, text="LCCN Source", variable=self.output_value_lccn_source, style='TCheckbutton').pack(anchor='w', padx=5, pady=2)
        #self.output_file_path = None
        
    def toggle_ui_for_search(self, is_searching):
        """
        Toggle the user interface elements based on the search state.
        
        Args:
            is_searching (bool): The state indicating whether a search is in progress.
        """
        if is_searching:
            # Hide all main UI elements to focus on the search.
            ui_elements = [self.top_frame, self.output_frame, self.start_button, 
                        self.open_log_button, self.choose_output_file_button, 
                        self.set_priority_button,self.open_output_file_button,self.clear_log_button]
            for element in ui_elements:
                element.pack_forget()


            # Configure and display the stop button and searching status.
            self.stop_button.pack(side='left', padx=5)
            self.stop_button['state'] = 'normal'
            self.search_status_var.set("Searching...")
            self.search_status_label.pack(side='top', pady=(20, 0), expand=True)
            self.stop_button['state'] = 'normal' 
            self.stop_button.pack(side='top', pady=(10, 0))
        else:
            # Stop any ongoing animation and hide the search status label and stop button.
            self.search_in_progress = False
            self.search_status_label.pack_forget()
            self.stop_button.pack_forget()

            # Restore UI elements to their initial state
            self.button_frame.pack_forget()
            self.setup_ui() # This method should repack all UI elements as required

    def animate_search_status(self, initial_message):
        """
        Update the search status label with an animated message.

        Args:
            initial_message (str): The initial part of the search status message.
        """
        def update_message():
            dot_count = 0
            while self.search_in_progress:
                # Calculate elapsed time
                elapsed_time = time.time() -self.search_start_time
                elapsed_time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))

                self.search_status_var.set(f"{self.current_identifier}/{self.total_identifiers}\n{initial_message}{'.' * dot_count}\nElapsed Time: {elapsed_time_str}")
                dot_count = (dot_count + 1) % 4
                time.sleep(0.5)  # Wait before updating again to avoid high CPU usage

        # Start the thread only if a search is in progress to avoid unnecessary threads.
        if self.search_in_progress:
            threading.Thread(target=update_message, daemon=True).start() 
    
    def initialize_sources(self):
        """Initialize source API objects in separate threads."""
        sources = {
            "Google Books (API)": GoogleBooksAPI,
            "Harvard Library (API)": HarvardLibraryAPI,
            "Library of Congress (API)": LibraryOfCongressAPI,
            "Open Library (API)": OpenLibraryAPI,
            "Columbia Library (Blacklight)": ColumbiaLibraryAPI,
            "Cornell Library (Blacklight)": CornellLibraryAPI,
            "Duke Library (Blacklight)": DukeLibraryAPI,
            "Indiana Library (Blacklight)": IndianaLibraryAPI,
            "Johns Hopkins Library (Blacklight)": JohnsHopkinsLibraryAPI,
            "North Carolina State Library (Blacklight)": NorthCarolinaStateLibraryAPI,
            "Pennsylvania State Library (Blacklight)": PennStateLibraryAPI,
            "Yale Library (Blacklight)": YaleLibraryAPI,
            "Stanford Library (Blacklight)": StanfordLibraryAPI
        }
        
        for key, api_class in sources.items():
            try:
                api_instance = api_class()  # Instantiate the API class
                self.source_mapping[key] = api_instance  # Add instance to source mapping
            except RuntimeError as e:
                logging.error(f"WebDriver error initializing {key}: {e}\nPlease make sure Google Chrome and ChromeDriver are installed and updated.")
                messagebox.showerror("Initialization Error", f"An error occurred initializing {key}. Please make sure Google Chrome is installed and up to date.")
                break  # Stop further initialization
            except Exception as e:
                logging.error(f"An error occurred initializing {key}: {e}")
                messagebox.showerror("Initialization Error", f"An unspecified error occurred initializing {key}. Please check your setup.")
                break  # Stop further initialization



    def browse_file(self):
        """Open a dialog for the user to select an input file."""
        filename = filedialog.askopenfilename()
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)

    def get_existing_data(self, identifier, file_type):
        """Retrieve existing data from the database based on the identifier and file type."""
        # Prepare initial data structure
        existing_data = {}

        # Format database query condition based on file type
        condition = f"Isbn = '{identifier}'" if file_type == 'ISBN' else f"Ocn = '{identifier}'"
        logging.info(f"Querying database for {file_type} {identifier}.")

        # Fetch and unpack book data
        book_data = self.db_manager.fetch_data("books", f"WHERE {condition}")
        if book_data:
            isbn, ocn = book_data[0][:2]  # Unpack first row's ISBN and OCN
            found_items = []
            if isbn:
                existing_data['isbn'] = [isbn]
                found_items.append(f"ISBN={isbn}")
            if ocn:
                existing_data['ocn'] = ocn
                found_items.append(f"OCN={ocn}")
            if found_items:
                logging.info(f"Found database record for {file_type} {identifier}: " + ', '.join(found_items))
            else:
                logging.info(f"Record found for {file_type} {identifier} but no ISBN or OCN data available.")
        else:
            logging.info(f"No database record found for {file_type} {identifier}.")

        # Determine correct ISBN identifier for LCCN data retrieval based on file_type
        lccn_identifier = existing_data.get('isbn', [''])[0] if file_type == 'ISBN' or 'isbn' in existing_data else ''
        if not lccn_identifier and file_type == 'OCN':  # Resolve ISBN for OCN if not already found
            book_data_from_ocn = self.db_manager.fetch_data("books", f"WHERE Ocn = '{identifier}'")
            if book_data_from_ocn:
                lccn_identifier = book_data_from_ocn[0][0]  # Assuming ISBN is the first column

        # Fetch and compile LCCN data if necessary
        if lccn_identifier and (self.output_value_lccn.get() or self.output_value_lccn_source.get()):
            lccn_query = f"JOIN book_lccn ON lccn.Lccn_id = book_lccn.Lccn_id WHERE book_lccn.Isbn = '{lccn_identifier}'"
            lccn_data = self.db_manager.fetch_data("lccn", lccn_query)
            if lccn_data:
                # Update here to only fetch the first LCCN and LCCN source
                first_lccn_row = lccn_data[0]  # Assuming the first row has the necessary data
                existing_data['lccn'] = [str(first_lccn_row[1])] if first_lccn_row[1] else None
                existing_data['lccn_source'] = [str(first_lccn_row[2])] if first_lccn_row[2] else None
                if existing_data['lccn']:
                    logging.info(f"LCCN data found for {file_type} {identifier}: {existing_data['lccn']}")
                if existing_data['lccn_source']:
                    logging.info(f"LCCN Source data found for {file_type} {identifier}: {existing_data['lccn_source']}")
            else:
                logging.info(f"No LCCN data found for {file_type} {identifier}.")


        return existing_data
    
    def write_data_to_output_file(self, identifier, data):
        """
        Writes the collected metadata for a given identifier to the configured output file.
        
        This method compiles data into a format consistent with user-selected options and 
        writes this information into a tab-delimited file. If the file doesn't exist, it will be created. 
        If it does, data will be appended. This method considers user settings to determine 
        which data should be included in the output file, such as ISBN, OCN, LCCN, and LCCN Source.

        Args:
            identifier (str): The unique identifier for the item being processed. 
                            This could be an ISBN, OCN, or any other defined identifier.
            data (dict): A dictionary containing metadata for the item associated 
                        with the identifier. Keys should match the user-selected 
                        output options (e.g., 'isbn', 'ocn', 'lccn', 'lccn_source').

        Returns:
            None: The function performs file I/O operations and does not return a value. 
                It logs a message upon successful writing of the data.
        """
        if not hasattr(self, 'output_file_path') or not self.output_file_path:
            return
        
        # Determine data type based on user selection
        input_type = 'ISBN' if self.input_file_type.get() == 1 else 'OCN'

        # Initialize headers based on user selections
        headers = []
        if self.output_value_isbn.get():
            headers.append('ISBN')
        if self.output_value_ocn.get():
            headers.append('OCN')
        if self.output_value_lccn.get():
            headers.append('LCCN')
        if self.output_value_lccn_source.get():
            headers.append('LCCN_Source')


        # Write data to file, creating it if necessary
        file_exists = os.path.isfile(self.output_file_path) and os.path.getsize(self.output_file_path) > 0
        with open(self.output_file_path, 'a', newline='') as file:
            # Change to csv.writer with delimiter as tab
            tsv_writer = csv.writer(file, delimiter='\t')
            if not file_exists:
                tsv_writer.writerow(headers)

            # Prepare the data row based on the chosen options
            row_data = []
            for header in headers:
                if header == 'ISBN':
                    # Ensure isbn_data is a list; if identifier is a single ISBN (str), convert it to a list
                    isbn_data = [identifier] if input_type == 'ISBN' else data.get('isbn', [])
                    # Remove any potential non-string or empty elements
                    isbn_data = [str(isbn) for isbn in isbn_data if isbn]
                    # Join the ISBN data, ensuring all elements are strings
                    #formatted_data = '; '.join(isbn_data)
                    formatted_data = isbn_data[0] if isbn_data else ''
                elif header == 'OCN':
                    # Ensure OCN data is extracted properly; default to an empty list if not found
                    ocn_data = identifier if input_type == 'OCN' else data.get('ocn', '')
                    # Assuming OCN is always a single value, take the first element, if available
                    formatted_data = str(ocn_data) if ocn_data else ''
                elif header == 'LCCN':
                    # Extract LCCN data, ensuring it's in list form
                    lccn_data = data.get('lccn', [])
                    # Remove any potential non-string or empty elements
                    lccn_data = [str(lccn) for lccn in lccn_data if lccn]
                    # Join the LCCN data
                    #formatted_data = '; '.join(lccn_data)
                    formatted_data = lccn_data[0] if lccn_data else ''
                elif header == 'LCCN_Source':
                    # Similarly handle LCCN source data
                    lccn_source_data = data.get('lccn_source', [])
                    lccn_source_data = [str(source) for source in lccn_source_data if source]
                    #formatted_data = '; '.join(lccn_source_data)
                    formatted_data = lccn_source_data[0] if lccn_source_data else ''
                else:
                    continue 
                
                row_data.append(formatted_data)
            
            row_data = [item if item not in [None, 'None'] else '' for item in row_data]
            # Check if all elements are empty, if not then write to the file
            if any(row_data):
                tsv_writer.writerow(row_data)
                logging.info(f"Write completed for {input_type} {identifier}")
                self.last_processed = identifier
    
    def start_search(self):
        """Validate output options and start the search process."""
        if sum([self.output_value_isbn.get(), self.output_value_ocn.get(), self.output_value_lccn.get(), self.output_value_lccn_source.get()]) <= 1:
            messagebox.showwarning("Warning", "Please choose more than one output option to start the search.")
            return

        file_type = 'ISBN' if self.input_file_type.get() == 1 else 'OCN'
        validation_result, data = verifyFileFormat(self.file_entry.get(), file_type)
        
        if validation_result == 'Invalid':
            messagebox.showerror("Error", "Invalid file format or contents. Please check the file.")
            return

        if not self.priority_list:
            messagebox.showwarning("Warning", "Please set the searching priority before starting the search.")
            return
        
        if not self.output_file_path:
            messagebox.showwarning("Warning", "Please set the output file path")
            return
        
        if os.path.exists(self.output_file_path) and os.path.getsize(self.output_file_path) > 0:
            # Prompt the user about overwriting the file
            overwrite = messagebox.askyesno("Confirm Overwrite", "The output file already has content. Do you wish to overwrite it?")
            if not overwrite:
                # User chose not to overwrite; cancel the search start
                messagebox.showinfo("Search Cancelled", "Search cancelled by user.")
                return
            else:
                with open(self.output_file_path, 'w') as file:
                    pass

        logging.info(f"Search started for {file_type} with {len(data)} items and priority list: {self.priority_list}")

        self.toggle_ui_for_search(True)
        self.search_start_time = time.time()
        self.search_active = True
        self.search_in_progress = True
        self.search_thread = threading.Thread(target=self.perform_search, args=(data,), daemon=True)
        self.search_thread.start()
        
    def perform_search(self, data):
        """Perform the search operation based on the provided data."""
        self.total_identifiers = len(data)
        self.animate_search_status("Searching")
        self.search_in_progress = True

        output_options = {
        'isbn': self.output_value_isbn.get(),
        'ocn': self.output_value_ocn.get(),
        'lccn': self.output_value_lccn.get(),
        'lccn_source': self.output_value_lccn_source.get()
                }
        
        input_type = 'isbn' if self.input_file_type.get() == 1 else 'ocn'
        
        for index,identifier in enumerate(data):
            self.current_identifier = index + 1
            logging.info(f"{index}/{self.total_identifiers}. Searching metadata for {identifier}")
            
            if not self.search_active: # Check if the search was stopped
                break
                 
            # Fetch existing data for the identifier
            existing_data = self.get_existing_data(identifier, 'ISBN' if self.input_file_type.get() == 1 else 'OCN')

            # Ensure that the identifier is properly represented in existing_data
            if input_type == 'isbn':
                # If the identifier is not already in the list, add it; otherwise, keep the existing list.
                existing_data['isbn'] = [str(identifier)] if str(identifier) not in existing_data.get('isbn', []) else existing_data.get('isbn', [])
            elif input_type == 'ocn':
                # Set the OCN to the identifier if it's different; otherwise, keep the existing OCN.
                existing_data['ocn'] = str(identifier) if existing_data.get('ocn', '') != str(identifier) else existing_data.get('ocn', '')

            # Update existing data based on missing fields and priority list
            self.fetch_and_update_missing_data(existing_data, identifier, input_type, output_options)

            # Write updated data to the output file and database
            self.update_database_with_existing_data(identifier, existing_data, input_type)
            self.write_data_to_output_file(identifier, existing_data)

        if self.search_active:
            logging.info(f"Search thread completed successfully for {len(data)} items.")
            self.finalize_search()
        else:
            logging.info(f"Search thread stopped manually after processing {self.current_identifier} out of {len(data)} items.")

    def finalize_search(self,manually_stopped=None):
        """Finalize the search operation by resetting states and notifying the user."""
        self.search_active = False
        self.toggle_ui_for_search(False)
        if self.search_start_time:
            self.search_total_time = time.time() - self.search_start_time  # Calculate total time
            total_time_str = time.strftime("%H:%M:%S", time.gmtime(self.search_total_time))
            if manually_stopped:
                logging.info("Search stopped manually")
                last_processed_info = f"\nLast identifier processed: {self.last_processed}." if self.last_processed else ""
                messagebox.showinfo("Search Stopped", f"Search stopped manually at {total_time_str}.\nProcessed {self.current_identifier - 1}/{self.total_identifiers}.{last_processed_info}")
            else:
                logging.info("Search completed")
                messagebox.showinfo("Search Completed", f"Search completed in {total_time_str}.")
        else:
            if manually_stopped:
                logging.info("Search stopped manually")
                last_processed_info = f"\nLast identifier processed: {self.last_processed}." if self.last_processed else ""
                messagebox.showinfo("Search Stopped", f"Search stopped manually.\nProcessed {self.current_identifier - 1}/{self.total_identifiers}.{last_processed_info}")
            else:
                logging.info("Search completed")
                messagebox.showinfo("Search Completed", "Search completed.")
        self.current_identifier = 0
        self.last_processed = None

    def fetch_and_update_missing_data(self, existing_data, identifier, input_type, output_options):
        """
        Fetches missing metadata for a given identifier from various data sources 
        based on a priority list and updates the existing data accordingly.

        This method iterates over the priority list of sources and queries each 
        source for missing metadata. When new data is found, it updates the existing 
        data structure. The search for missing data continues until all data is found 
        or all sources have been queried.

        Args:
            existing_data (dict): The current set of metadata associated with the identifier.
            identifier (str): The unique identifier for the metadata subject (e.g., ISBN, OCN).
            input_type (str): The type of the identifier (e.g., 'ISBN', 'OCN').
            output_options (dict): A dictionary specifying which types of data to fetch.

        Returns:
            None: The function updates the existing_data dictionary in-place and does not return anything.
        """
        effective_output_options = output_options.copy()
        effective_output_options.pop(input_type, None)

        missing_data = {key for key, value in effective_output_options.items() if value and key.lower() not in existing_data}

        if missing_data:
            for source_name in self.priority_list:
                if not self.search_active: # Check if the search was stopped
                    return
                source = self.source_mapping.get(source_name)
                if not source:
                    continue

                logging.info(f"Querying {source_name} for missing data for identifier: {identifier}")


                try:
                    result = source.fetch_metadata(identifier, input_type)
                except Exception as e:
                    logging.error(f"Error fetching metadata from {source_name} for {identifier}: {e}")
                    continue  # Proceed to the next source if there's an error

                if not self.search_active: # Check if the search was stopped
                    return
                if not result: continue

                # Update the existing data if new data is found
                updated = False
                for data_type in missing_data.copy():  # Iterate over a copy to modify original safely
                    if data_type in result and result[data_type]:
                        if isinstance(result[data_type], (str, list)) and not result[data_type]:
                            continue
                        
                        existing_data[data_type] = result[data_type.lower()]
                        missing_data.remove(data_type)
                        updated = True

                if updated:
                    logging.info(f"Updated data for {identifier} from {source_name}")

                    if not missing_data:  # Exit early if all missing data has been found
                        break


    def update_database_with_existing_data(self, identifier, data, input_type):
        """
        Update the database with the collected data for a given identifier.

        Args:
            identifier (str): The identifier for the data (ISBN or OCN).
            data (dict): The data to be updated in the database.
            input_type (str): The type of identifier ('isbn' or 'ocn').
        """
        # Normalize ISBNs to a list for uniform processing
        isbns = data.get('isbn', [])
        ocn = data.get('ocn', '')
        lccns = data.get('lccn', [])
        lccn_sources = data.get('lccn_source', [])

        # Update book records
        for isbn in isbns:
            self._update_book_records(isbn, ocn)
        
        # Update LCCN records only once per ISBN to avoid redundancy
        self._update_lccn_records(isbns, lccns, lccn_sources)

    def _process_book_identifiers(self, isbn_str, ocn_str):
        """
        Process and validate book identifiers.

        Args:
            isbn_str (str): The ISBN string to process.
            ocn_str (str): The OCN string to process.

        Returns:
            tuple: A tuple containing the processed ISBN and OCN as strings.
        """
        isbn = isbn_str.strip() if isbn_str else None
        ocn = ocn_str.strip() if ocn_str else None
        return isbn, ocn



    def _update_book_records(self, isbn, ocn):
        """
        Insert or update the book records in the database based on an ISBN and OCN.

        Args:
            isbn (str): The ISBN of the book.
            ocn (str): The OCN of the book.
        """
        if not self.db_manager.data_exists('books', f"Isbn = '{isbn}'"):
            self.db_manager.insert_data('books', (isbn, ocn))
        elif ocn:
            existing_ocn = self.db_manager.fetch_data('books', f"WHERE Isbn = '{isbn}'")[0][1]
            if existing_ocn != ocn:
                self.db_manager.update_data('books', f"Ocn = '{ocn}'", f"Isbn = '{isbn}'")

    def _update_lccn_records(self, isbns, lccns, lccn_sources):
        """
        Update the LCCN records associated with books in the database.

        Args:
            isbns (list): The list of ISBNs of the books.
            lccns (list): A list of LCCNs associated with the books.
            lccn_sources (list): A list of sources corresponding to each LCCN.
        """
        for lccn, source in zip(lccns, lccn_sources):
            if not self.db_manager.data_exists('lccn', f"Lccn = '{lccn}'"):
                self.db_manager.insert_data('lccn', (None, lccn, source))
                lccn_id = self.db_manager.fetch_data('lccn', f"WHERE Lccn = '{lccn}'")[0][0]
            else:
                lccn_id = self.db_manager.fetch_data('lccn', f"WHERE Lccn = '{lccn}'")[0][0]
            
            for isbn in isbns:
                if not self.db_manager.data_exists('book_lccn', f"Isbn = '{isbn}' AND Lccn_id = {lccn_id}"):
                    self.db_manager.insert_data('book_lccn', (isbn, lccn_id))
    def choose_output_file(self):
        """Prompt the user to select a file path for saving the output data in TSV format."""
        file_options = {
            "mode": 'w',
            "defaultextension": ".tsv",
            "filetypes": [("TSV Files", "*.tsv"), ("All Files", "*.*")]
        }
        file = asksaveasfile(**file_options)
        if file:  # True if the dialog is not canceled.
            self.output_file_path = file.name
            messagebox.showinfo("Success", f"Output TSV file selected: {self.output_file_path}")
            file.close()  # Close the file after saving the path.

    def open_output_file(self):
        """Open the output file with the default application, cross-platform."""
        if self.output_file_path and os.path.exists(self.output_file_path):
            if sys.platform.startswith('darwin'):  # macOS
                subprocess.run(['open', self.output_file_path], check=True)
            elif sys.platform.startswith('win32'):  # Windows
                os.startfile(self.output_file_path)
            elif sys.platform.startswith('linux'):  # Linux
                subprocess.run(['xdg-open', self.output_file_path], check=True)
            else:
                messagebox.showerror("Error", "Unsupported OS")
        else:
            messagebox.showwarning("Warning", "No output file has been set or the file does not exist.")


    def set_priority(self):
        """Open a new window to set the search priority."""
        priority_window = tk.Toplevel(self)
        window_attributes = {
        'width': self.app_width,
        'height': self.app_height,
        'x': self.app_x,
        'y': self.app_y,
         }
        
        PriorityList(priority_window, self.update_priority_lists, self.priority_list, self.unused_sources, window_attributes)

    def update_priority_lists(self, selected, unused):
        """Update the internal priority list for searches."""
        self.priority_list = selected
        self.unused_sources = unused
        logging.info(f"Updated selected sources: {self.priority_list}")
        logging.info(f"Updated unused sources: {self.unused_sources}")
        self.save_source_lists()
    

    def save_source_lists(self):
        data = {
            'selected_sources': self.priority_list,
            'unused_sources': self.unused_sources
        }
        app_data_dir = self.get_app_data_directory()
        filepath = app_data_dir / 'source_lists.json'
        with open(filepath, 'w') as file:
            json.dump(data, file)

    def load_source_lists(self):
        app_data_dir = self.get_app_data_directory()
        filepath = app_data_dir / 'source_lists.json'
        try:

            if os.path.getsize(filepath) == 0:
                raise json.JSONDecodeError("File is empty", "", 0)


            with open(filepath, 'r') as file:
                data = json.load(file)
                selected_sources = data.get('selected_sources', [])
                unused_sources = data.get('unused_sources', [])
                # Safeguard to ensure all sources are included
                all_sources = set(self.priority_list + self.unused_sources)
                file_sources = set(selected_sources + unused_sources)
                
                if not all_sources == file_sources:
                    # If not all sources are present, reinitialize the file
                    self.save_source_lists()
                else:
                    self.priority_list = selected_sources
                    self.unused_sources = unused_sources
        except Exception as e:
            # If the file doesn't exist or is empty, save the initial lists to create the file.
            self.save_source_lists()


    def open_log(self):
        """Open a new window to display the application's log file content."""
        if self.log_window_open:
            return  # Exit the function if the log window is already open

        try:
            self.log_window = tk.Toplevel(self)
            self.log_window.title("Log Viewer")
            self.log_text_widget = tk.scrolledtext.ScrolledText(self.log_window, wrap="word")
            self.log_text_widget.pack(fill="both", expand=True)
            self.update_log_content(initial=True)
            self.log_window_open = True  # Indicate that the log window is now open

            # Handle the log window's closure
            self.log_window.protocol("WM_DELETE_WINDOW", self.on_log_window_close)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open log: {str(e)}")

    def update_log_content(self,initial=False):
        """Append only new content to the log file displayed in the text widget."""
        try:
            current_size = os.path.getsize(self.log_file_path)
            new_content_size = current_size - self.log_file_last_size

            if new_content_size > 0:
                with open(self.log_file_path, 'r') as log_file:
                    log_file.seek(self.log_file_last_size)  # Move to the last known position
                    new_content = log_file.read()  # Read only new content
                    self.log_text_widget.config(state=tk.NORMAL)  # Ensure the widget is writable
                    self.log_text_widget.insert(tk.END, new_content)  # Append new content
                    if initial:
                        self.log_text_widget.see(tk.END)
                    self.log_text_widget.config(state=tk.DISABLED)  # Optional: make the widget readonly again
                    self.log_file_last_size = current_size  # Update the last known size

        except Exception as e:
            logging.error(f"Failed to update log content: {str(e)}")

        self.log_text_widget.after(1000, self.update_log_content)

    def on_log_window_close(self):
        """Handle the log window's closure."""
        self.log_window_open = False  # Reset the flag when the window is closed
        self.log_window.destroy()


    def clear_log(self):
        try:
            with open(self.log_file_path, 'w') as log_file:
                log_file.truncate(0)
            logging.info("Log file cleared.")
            messagebox.showinfo("Log Cleared", "The log file has been successfully cleared.")
        except Exception as e:
            logging.error(f"Failed to clear log: {str(e)}")
            messagebox.showerror("Error", f"Failed to clear log: {str(e)}")


    
if __name__ == "__main__":
    app = LibraryMetadataHarvesterApp()
    app.mainloop()
