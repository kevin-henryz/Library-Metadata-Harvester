""" 
"Cornell": CornellLibraryAPI(),
"Duke": DukeLibraryAPI()
"Indiana": IndianaLibraryAPI(),
"Johns Hopkins": JohnsHopkinsLibraryAPI(),
"North Carolina State": NorthCarolinaStateAPI(),
"Penn State": PennStateLibraryAPI()
"Yale": YaleLibraryAPI(),
"Stanford": StanfordLibraryAPI()
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.filedialog import asksaveasfile
import os
import logging
import threading
import time
import csv
from util.file_processor import read_and_validate_file
from gui.priority_list import PriorityListApp
from db.database_manager import DatabaseManager
from apis.harvard_library_API import HarvardAPI
from apis.library_of_congress_API import LibraryOfCongressAPI
from apis.google_books_API import GoogleBooksAPI
from webScraping.columbia_library_api import ColumbiaLibraryAPI

class LibraryMetadataHarvesterApp(tk.Tk):
    """A GUI application for harvesting library metadata from different sources."""

    source_mapping = {
        "Harvard Library API": HarvardAPI(),
        "Library of Congress API": LibraryOfCongressAPI(),
        "Google Books API": GoogleBooksAPI(),
        "Columbia Library": ColumbiaLibraryAPI()
        }
    

    def __init__(self):
        """Initialize the application, its variables, and UI components."""
        super().__init__()

        self.configure_app()
        self.setup_logging(os.path.join('src', 'logs', 'example.log'))
        self.initialize_database()
        self.setup_ui()
        self.priority_list = []
        self.search_status_var = tk.StringVar(self)
        self.search_status_label = tk.Label(self, textvariable=self.search_status_var, font=("Helvetica", 16), bg='#202020', fg='white')
        self.search_active = False
        self.total_identifiers = 0
        self.current_identifier = 0


    def configure_app(self):
        """Configure the main window settings and styles."""
        self.title('Library Metadata Harvester')
        self.configure(bg='#202020') 
        self.geometry('600x300') 
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TButton', background='#404040', foreground='white', borderwidth=1)
        self.style.configure('TFrame', background='#202020')
        self.style.configure('TCheckbutton', background='#202020', foreground='white')
        self.style.configure('TRadioButton', background='#202020', foreground='white')
        self.style.configure('TLabel', background='#202020', foreground='white')
        self.style.configure('TEntry', background='#404040', foreground='white', fieldbackground='#404040', borderwidth=1)
        self.style.map('TEntry', fieldbackground=[('focus', '#404040')], foreground=[('focus', 'white')])


    def setup_logging(self, log_file_path):
        """Setup application logging."""
        logging.getLogger().handlers.clear()
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            handlers=[
                                logging.FileHandler(log_file_path),
                                logging.StreamHandler()
                            ])
        logging.info("Application started")

    def initialize_database(self):
        """Initialize the application's database and required tables."""
        self.db_manager = DatabaseManager()
        self.db_manager.create_table("books", "Isbn INTEGER PRIMARY KEY, Ocn INTEGER")
        self.db_manager.create_table("lccn", "Lccn_id INTEGER PRIMARY KEY AUTOINCREMENT, Lccn TEXT, Source TEXT")
        self.db_manager.create_table("book_lccn", "Isbn INTEGER, Lccn_id INTEGER, FOREIGN KEY (Isbn) REFERENCES books (Isbn), FOREIGN KEY (Lccn_id) REFERENCES lccn (Lccn_id)")

    def setup_ui(self):
        """Setup the user interface for the application."""
        self.setup_top_frame()
        self.setup_output_options()
        self.setup_input_frame()
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
        self.input_frame.pack(side='left', fill='x', padx=5, pady=5) 
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
        self.start_button = ttk.Button(self.button_frame, text="Start Search", command=self.start_search)
        self.start_button.pack(side='left', padx=5)
        self.stop_button = ttk.Button(self.button_frame, text="Stop Search", command=self.finalize_search, state='disabled')
        self.open_log_button = ttk.Button(self.button_frame, text="Open Log", command=lambda: self.open_log(os.path.join('src', 'logs', 'example.log')))
        self.open_log_button.pack(side='left', padx=5)
        self.choose_output_file_button = ttk.Button(self.button_frame, text="Choose Output File", command=self.choose_output_file)
        self.choose_output_file_button.pack(side='left', padx=5)
        self.set_priority_button = ttk.Button(self.button_frame, text="Set Searching Priority", command=self.set_priority)
        self.set_priority_button.pack(side='left', padx=5)
   
    def setup_output_options(self):
        """Setup the frame for output options."""
        self.output_frame = ttk.Frame(self.top_frame, style='TFrame')
        self.output_frame.pack(side='right', anchor='e', padx=10, pady=5)
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
        self.output_file_path = None
        
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
                        self.set_priority_button]
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
                # Update the status message with a rotating number of dots for a visual effect.
                time.sleep(0.5)
                self.search_status_var.set(f"{self.current_identifier}/{self.total_identifiers}\n{initial_message}{'.' * dot_count}")
                dot_count = (dot_count + 1) % 4 
        # Start the thread only if a search is in progress to avoid unnecessary threads.
        if self.search_in_progress:
            threading.Thread(target=update_message, daemon=True).start() 
    
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
        condition = f"Isbn = {identifier}" if file_type == 'ISBN' else f"Ocn = {identifier}"
        logging.info(f"Looking for {file_type} {identifier} in the database.")

        # Fetch and unpack book data
        book_data = self.db_manager.fetch_data("books", f"WHERE {condition}")
        if book_data:
            existing_data['isbn'], existing_data['ocn'] = book_data[0][:2]  # Unpack first row's ISBN and OCN
            logging.info(f"Found database record for {file_type} {identifier}: ISBN={existing_data['isbn']}, OCN={existing_data['ocn']}")
        else:
            logging.info(f"No database record found for {file_type} {identifier}.")

        # Fetch and compile LCCN data if necessary
        if self.output_value_lccn.get() or self.output_value_lccn_source.get():
            lccn_data = self.db_manager.fetch_data("book_lccn", f"JOIN lccn ON book_lccn.Lccn_id = lccn.Lccn_id WHERE book_lccn.Isbn = {identifier}")
            if lccn_data:
                existing_data['lccn'] = [str(row[1]) for row in lccn_data]  # Convert LCCN to string to avoid type issues
                existing_data['lccn_source'] = [row[2] for row in lccn_data]

        return existing_data
    
    def write_data_to_output_file(self, identifier, data):
        """Write the collected data to the specified output file."""
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
            headers.append('LCCN Source')

        # Write data to file, creating it if necessary
        file_exists = os.path.isfile(self.output_file_path) and os.path.getsize(self.output_file_path) > 0
        with open(self.output_file_path, 'a', newline='') as file:
            csv_writer = csv.writer(file)
            if not file_exists:
                csv_writer.writerow(headers)

            # Prepare the data row based on the chosen options
            row_data = []
            for header in headers:
                if header == 'ISBN':
                    isbn_data = identifier if input_type == 'ISBN' else data.get('isbn', [])
                elif header == 'OCN':
                    ocn_data = identifier if input_type == 'OCN' else data.get('ocn', [])
                elif header == 'LCCN':
                    lccn_data = data.get('lccn', [])
                elif header == 'LCCN Source':
                    lccn_source_data = data.get('lccn_source', [])
                else:
                    continue  # Skip unknown headers
                
                # Convert the data to string, join list items if necessary, and add to the row data
                current_data = locals().get(f"{header.lower()}_data", '')
                formatted_data = '; '.join(map(str, current_data)) if isinstance(current_data, list) else str(current_data)
                row_data.append(formatted_data)

            row_data = [item if item not in [None, 'None'] else '' for item in row_data]
            # Check if all elements are empty, if not then write to the file
            if any(row_data):
                csv_writer.writerow(row_data)
                logging.info(f"Write completed for {input_type} {identifier}")

    def start_search(self):
        """Validate output options and start the search process."""
        if sum([self.output_value_isbn.get(), self.output_value_ocn.get(), self.output_value_lccn.get(), self.output_value_lccn_source.get()]) <= 1:
            messagebox.showwarning("Warning", "Please choose more than one output option to start the search.")
            return

        file_type = 'ISBN' if self.input_file_type.get() == 1 else 'OCN'
        validation_result, data = read_and_validate_file(self.file_entry.get(), file_type)
        
        if validation_result == 'Invalid':
            messagebox.showerror("Error", "Invalid file format or contents. Please check the file.")
            return

        if not self.priority_list:
            messagebox.showwarning("Warning", "Please set the searching priority before starting the search.")
            return
        
        if not self.output_file_path:
            messagebox.showwarning("Warning", "Please set the output file path")
            return

        logging.info(f"Search started for {file_type} with {len(data)} items and priority list: {self.priority_list}")

        self.toggle_ui_for_search(True)
        self.search_active = True
        self.search_in_progress = True
        threading.Thread(target=self.perform_search, args=(data,), daemon=True).start()
        
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
                return
                 
            # Fetch existing data for the identifier
            existing_data = self.get_existing_data(identifier, 'ISBN' if self.input_file_type.get() == 1 else 'OCN')

            # Update existing data based on missing fields and priority list
            self.fetch_and_update_missing_data(existing_data, identifier, input_type, output_options)

            # Write updated data to the output file and database
            self.write_data_to_output_file(identifier, existing_data)
            self.update_database_with_existing_data(identifier, existing_data, input_type)

        
            
        self.finalize_search() # Encapsulate ending routines of the search

    def finalize_search(self):
        """Finalize the search operation by resetting states and notifying the user."""
        self.search_active = False
        self.toggle_ui_for_search(False)
        logging.info("Search completed")
        messagebox.showinfo("Search", "Search completed")


    def fetch_and_update_missing_data(self, existing_data, identifier, input_type, output_options):
        """Fetch missing metadata based on the priority list and update existing data."""
        missing_data = {key for key, value in output_options.items() if value and key not in existing_data}

        if missing_data:
            for source_name in self.priority_list:
                source = self.source_mapping.get(source_name)
                if not source:
                    continue

                result = source.fetch_metadata(identifier, input_type)
                if not result:
                    logging.info(f"No results found for identifier {identifier} from {source_name}")
                    continue

                # Update the existing data if new data is found
                updated = False
                for data_type in missing_data.copy():  # Iterate over a copy to modify original safely
                    if data_type.lower() in result:
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
        isbns = [isbns] if not isinstance(isbns, list) else isbns

        for isbn_str in isbns:
            isbn, ocn = self._process_book_identifiers(isbn_str, data.get('ocn'))
            if isbn:  # Proceed only if a valid ISBN is present
                self._update_book_records(isbn, ocn)
                self._update_lccn_records(isbn, data.get('lccn', []), data.get('lccn_source', []))

    def _process_book_identifiers(self, isbn_str, ocn_str):
        """
        Process and validate book identifiers.

        Args:
            isbn_str (str): The ISBN string to process.
            ocn_str (str): The OCN string to process.

        Returns:
            tuple: A tuple containing the processed ISBN and OCN, or None if invalid.
        """
        try:
            isbn = int(isbn_str)
        except (ValueError, TypeError):
            logging.error(f"Invalid ISBN format: {isbn_str}. Expected a numeric value.")
            return None, None  # Return None to skip this entry due to invalid ISBN

        # Validate and convert OCN if present
        ocn = None
        if ocn_str:
            try:
                ocn = int(ocn_str)
            except ValueError:
                logging.error(f"Invalid OCN format: {ocn_str}. Expected a numeric value.")
                # Continue with OCN as None if format is invalid

        return isbn, ocn


    def _update_book_records(self, isbn, ocn):
        """
        Insert or update the book records in the database based on ISBN and OCN.

        Args:
            isbn (int): The ISBN of the book.
            ocn (int): The OCN of the book.
        """
        if not self.db_manager.data_exists('books', f"Isbn = {isbn}"):
            self.db_manager.insert_data('books', (isbn, ocn))
        elif ocn is not None:
            self.db_manager.update_data('books', f"Ocn = {ocn}", f"Isbn = {isbn}")

    def _update_lccn_records(self, isbn, lccns, lccn_sources):
        """
        Update the LCCN records associated with a book in the database.

        Args:
            isbn (int): The ISBN of the book.
            lccns (list): A list of LCCNs associated with the book.
            lccn_sources (list): A list of sources corresponding to each LCCN.
        """
        for lccn, source in zip(lccns, lccn_sources):
            if not self.db_manager.data_exists('lccn', f"Lccn = '{lccn}'"):
                self.db_manager.insert_data('lccn', (None, lccn, source))
            lccn_id = self.db_manager.fetch_data('lccn', f"WHERE Lccn = '{lccn}'")[0][0]
            if not self.db_manager.data_exists('book_lccn', f"Isbn = {isbn} AND Lccn_id = {lccn_id}"):
                self.db_manager.insert_data('book_lccn', (isbn, lccn_id))

    def choose_output_file(self):
        """Prompt the user to select a file path for saving the output data in CSV format."""
        file_options = {
            "mode": 'w',
            "defaultextension": ".csv",
            "filetypes": [("CSV Files", "*.csv"), ("All Files", "*.*")]
        }
        file = asksaveasfile(**file_options)
        if file:  # True if the dialog is not canceled.
            self.output_file_path = file.name
            messagebox.showinfo("Success", f"Output CSV file selected: {self.output_file_path}")
            file.close()  # Close the file after saving the path.

    def set_priority(self):
        """Open a new window to set the search priority."""
        priority_window = tk.Toplevel(self)
        PriorityListApp(priority_window, self.update_priority_list)

    def update_priority_list(self, updated_list):
        """Update the internal priority list for searches."""
        self.priority_list = updated_list
        logging.info(f"Updated priority list: {self.priority_list}")

    def open_log(self, log_path):
        """Open a new window to display the application's log file content."""
        try:
            with open(log_path, 'r') as log_file:
                log_content = log_file.read()
                log_window = tk.Toplevel(self)
                log_window.title("Log Viewer")
                text = tk.Text(log_window, wrap="word")
                text.pack(fill="both", expand=True)
                text.insert(tk.END, log_content)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open log: {str(e)}")
    
if __name__ == "__main__":
    app = LibraryMetadataHarvesterApp()
    app.mainloop()
