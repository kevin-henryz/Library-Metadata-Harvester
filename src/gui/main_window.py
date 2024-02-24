import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.filedialog import asksaveasfile
import sys
import os
import logging
import threading
import time

import csv


src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from util.file_processor import read_and_validate_file
from gui.priority_list import PriorityListApp
from db.database_manager import DatabaseManager

#Test code
from gui.dummy_source import *

class LibraryMetadataHarvesterApp(tk.Tk):
    
    source_mapping = {
    "OCLC API": OCLCAPI(),
    "Library of Congress API": LibraryOfCongressAPI(),
    "Harvard Library API": HarvardLibraryAPI(),
    "Open Library API": OpenLibraryAPI(),
    "Google Books API": GoogleBooksAPI(),
    "Yale": YaleLibraryAPI(),
    "Columbia": ColumbiaLibraryAPI(),
    "University of Virginia": UniversityOfVirginiaLibraryAPI(),
    "Stanford": StanfordLibraryAPI(),
    "Johns Hopkins U": JohnsHopkinsULibraryAPI(),
    "Cornell": CornellLibraryAPI(),
    "NCSU": NCSULibraryAPI(),
    "Duke": DukeLibraryAPI(),
    "Penn State": PennStateLibraryAPI(),
    "Indiana U": IndianaULibraryAPI(),
    "McGill": McGillLibraryAPI(),
    "VOILA": VOILAAPI(),
}


    def __init__(self):
        super().__init__()

        self.configure_app()
        self.setup_logging('src/logs/example.log')
        self.initialize_database()
        self.setup_ui()
        self.priority_list = []
        self.search_status_var = tk.StringVar(self)
        self.search_status_label = tk.Label(self, textvariable=self.search_status_var, font=("Helvetica", 16), bg='#202020', fg='white')
        self.search_active = False
        self.total_identifiers = 0
        self.current_identifier = 0


    def configure_app(self):
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
        # Remove any existing handlers attached to the root logger
        logging.getLogger().handlers.clear()

        # Configure logging to write to a file and also print to stdout
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            handlers=[
                                logging.FileHandler(log_file_path),
                                logging.StreamHandler()
                            ])

        logging.info("Application started")

    def initialize_database(self):
        """Initialize the database and tables."""
        self.db_manager = DatabaseManager()
        self.db_manager.create_table("books", "Isbn INTEGER PRIMARY KEY, Ocn INTEGER")
        self.db_manager.create_table("lccn", "Lccn_id INTEGER PRIMARY KEY AUTOINCREMENT, Lccn TEXT, Source TEXT")
        self.db_manager.create_table("book_lccn", "Isbn INTEGER, Lccn_id INTEGER, FOREIGN KEY (Isbn) REFERENCES books (Isbn), FOREIGN KEY (Lccn_id) REFERENCES lccn (Lccn_id)")

    def get_existing_data(self, identifier, file_type):
        # Initialize an empty dictionary to hold found data
        existing_data = {}
        if file_type == 'ISBN':
            condition = f"Isbn = {identifier}"
        else: # Assuming OCN for simplicity; adjust as needed for your application
            condition = f"Ocn = {identifier}"
        
        # Check for main book data (ISBN, OCN)
        book_data = self.db_manager.fetch_data("books", f"WHERE {condition}")
        if book_data:
            existing_data['ISBN'] = book_data[0][0]  # Assuming first column is ISBN
            existing_data['OCN'] = book_data[0][1]  # Assuming second column is OCN
        
        # Check for LCCN data if required
        if self.output_value_lccn.get() or self.output_value_lccn_source.get():
            lccn_data = self.db_manager.fetch_data("book_lccn", f"JOIN lccn ON book_lccn.Lccn_id = lccn.Lccn_id WHERE book_lccn.Isbn = {identifier}")
            if lccn_data:
                existing_data['LCCN'] = [row[1] for row in lccn_data]  # Assuming LCCN is in the second column
                existing_data['LCCN Source'] = [row[2] for row in lccn_data]  # Assuming source is in the third column
        
        return existing_data
    
    def write_data_to_output_file(self, identifier, data):
        # Ensure the output file path is defined
        if not hasattr(self, 'output_file_path') or not self.output_file_path:
            messagebox.showerror("Error", "Output file path is not set.")
            return

        # Open the file in append mode, so we add to the file without overwriting it
        with open(self.output_file_path, 'a', newline='') as file:
            # Use csv.writer to handle the CSV output
            csv_writer = csv.writer(file)
            
            # Prepare the row data starting with the identifier
            row_data = [identifier]
            
            # Append each chosen option's data to the row
            # The order of fields will match the order in which they are checked and appended here
            if self.output_value_isbn.get():
                row_data.append(data.get('ISBN', ''))
            if self.output_value_ocn.get():
                row_data.append(data.get('OCN', ''))
            if self.output_value_lccn.get():
                row_data.append('; '.join(data.get('LCCN', [])))  # Join multiple LCCNs by semicolon
            if self.output_value_lccn_source.get():
                row_data.append('; '.join(data.get('LCCN Source', [])))  # Join multiple sources by semicolon
            
            # Write the row to the CSV file
            csv_writer.writerow(row_data)
            logging.info(f"Write completed")


    def setup_ui(self):
        self.setup_top_frame()
        self.setup_output_options()
        self.setup_input_frame()
        self.setup_buttons_frame()
        self.search_in_progress = False
        self.search_status_var = tk.StringVar(value="")
        self.search_status_label = tk.Label(self, textvariable=self.search_status_var, font=("Helvetica", 16), bg='#202020', fg='white')
        self.search_status_label.pack_forget()  # Initially hide it


    def setup_top_frame(self):
        self.top_frame = ttk.Frame(self, style='TFrame')
        self.top_frame.pack(side='top', fill='x', padx=5, pady=5)


    def setup_input_frame(self):
        self.input_frame = ttk.Frame(self.top_frame, style='TFrame')
        self.input_frame.pack(side='left', fill='x', padx=5, pady=5) 

        ttk.Label(self.input_frame, text="Data Type of Input File:",style='TLabel').grid(row=0, column=0, sticky='w')
        self.input_file_type = tk.IntVar(value=1)  # Default to ISBN
        ttk.Radiobutton(self.input_frame, text="ISBN", variable=self.input_file_type, value=1, style='TRadiobutton',command=self.update_checkbox_state).grid(row=2, column=0, sticky='w')
        ttk.Radiobutton(self.input_frame, text="OCN", variable=self.input_file_type, value=0, style='TRadiobutton',command=self.update_checkbox_state).grid(row=2, column=1, sticky='w')

        ttk.Label(self.input_frame, text="Browse Input File:", style='TLabel').grid(row=3, column=0, sticky='w', pady=(10, 0))
        self.file_entry = ttk.Entry(self.input_frame, width=40)
        self.file_entry.grid(row=4, column=0, sticky='w')
        ttk.Button(self.input_frame, text="Browse", command=self.browse_file).grid(row=4, column=1, padx=5)

    def update_checkbox_state(self):
        # Check and lock the corresponding checkbox based on the radio button selection
        if self.input_file_type.get() == 1:  # ISBN selected
            self.output_value_isbn.set(True)  # Check the ISBN checkbox
            self.output_value_ocn.set(False)
            # Disable the ISBN checkbox to prevent user interaction
            self.isbn_checkbutton['state'] = 'disabled'  
            # Enable the OCN checkbox in case it was previously disabled
            self.ocn_checkbutton['state'] = 'normal'
        else:  # OCN selected
            self.output_value_ocn.set(True)  # Check the OCN checkbox
            self.output_value_isbn.set(False)
            # Disable the OCN checkbox to prevent user interaction
            self.ocn_checkbutton['state'] = 'disabled'
            # Enable the ISBN checkbox in case it was previously disabled
            self.isbn_checkbutton['state'] = 'normal'



    def setup_buttons_frame(self):

        self.button_frame = ttk.Frame(self, style='TFrame')
        self.button_frame.pack(fill='x', padx=5, pady=10)

        self.start_button = ttk.Button(self.button_frame, text="Start Search", command=self.start_search)
        self.start_button.pack(side='left', padx=5)

        self.stop_button = ttk.Button(self.button_frame, text="Stop Search", command=self.stop_search, state='disabled')

        self.open_log_button = ttk.Button(self.button_frame, text="Open Log", command=lambda: self.open_log('src/logs/example.log'))
        self.open_log_button.pack(side='left', padx=5)
 
        self.choose_output_file_button = ttk.Button(self.button_frame, text="Choose Output File", command=self.choose_output_file)
        self.choose_output_file_button.pack(side='left', padx=5)

        self.set_priority_button = ttk.Button(self.button_frame, text="Set Searching Priority", command=self.set_priority)
        self.set_priority_button.pack(side='left', padx=5)
   
    def setup_output_options(self):
        self.output_frame = ttk.Frame(self.top_frame, style='TFrame')
        self.output_frame.pack(side='right', anchor='e', padx=10, pady=5)

        ttk.Label(self.output_frame, text="Output Options:", style='TLabel').pack(anchor='w')
        self.output_value_isbn = tk.BooleanVar()
        self.output_value_ocn = tk.BooleanVar()
        self.output_value_lccn = tk.BooleanVar()
        self.output_value_lccn_source = tk.BooleanVar()
        #self.output_value_doi = tk.BooleanVar()

        self.isbn_checkbutton = ttk.Checkbutton(self.output_frame, text="ISBN", variable=self.output_value_isbn, style='TCheckbutton')
        self.isbn_checkbutton.pack(anchor='w', padx=5, pady=2)
        self.isbn_checkbutton['state'] = 'disabled' 
        self.output_value_isbn.set(True) 
        self.ocn_checkbutton = ttk.Checkbutton(self.output_frame, text="OCN", variable=self.output_value_ocn, style='TCheckbutton')
        self.ocn_checkbutton.pack(anchor='w', padx=5, pady=2)
        ttk.Checkbutton(self.output_frame, text="LCCN", variable=self.output_value_lccn, style='TCheckbutton').pack(anchor='w', padx=5, pady=2)
        ttk.Checkbutton(self.output_frame, text="LCCN Source", variable=self.output_value_lccn_source, style='TCheckbutton').pack(anchor='w', padx=5, pady=2)
        #ttk.Checkbutton(self.output_frame, text="DOI", variable=self.output_value_doi, style='TCheckbutton').pack(anchor='w', padx=5, pady=2)

        self.output_file_path = None
        
    
    
    def browse_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filename)


    def start_search(self):
        # Validate output options
        if sum([self.output_value_isbn.get(), self.output_value_ocn.get(), self.output_value_lccn.get(), self.output_value_lccn_source.get()]) <= 1:
            messagebox.showwarning("Warning", "Please choose more than one output option to start the search.")
            return


        # Determine the file type based on the radio button selection
        file_type = 'ISBN' if self.input_file_type.get() == 1 else 'OCN'
        file_path = self.file_entry.get()
        
        # Validate and read the file
        validation_result, data = read_and_validate_file(file_path, file_type)
        if validation_result == 'Invalid':
            messagebox.showerror("Error", "Invalid file format or contents. Please check the file.")
            return


        # Make sure the priority list is set
        if not self.priority_list:
            messagebox.showwarning("Warning", "Please set the searching priority before starting the search.")
            return
        
        if not self.output_file_path:
            messagebox.showwarning("Warning", "Please set the output file path")
            return


        # Proceed with the search logic using the validated data and priority list
        logging.info(f"Search started for {file_type} with {len(data)} items and priority list: {self.priority_list}")

        self.toggle_ui_for_search(True)
        self.search_active = True
        threading.Thread(target=self.perform_search, args=(data,), daemon=True).start()
        
    def perform_search(self, data):
        total = len(data)
        self.total_identifiers = total
        self.animate_search_status("Searching")
        self.search_in_progress = True

        output_options = {
        'ISBN': self.output_value_isbn.get(),
        'OCN': self.output_value_ocn.get(),
        'LCCN': self.output_value_lccn.get(),
        'LCCN Source': self.output_value_lccn_source.get()
                }
        
        for index,identifier in enumerate(data):
            self.current_identifier = index + 1
            logging.info(f"{index}/{total}. Searching metadata for {identifier}")
            if not self.search_active:
                return  # Exit the loop if search has been stopped
            
            existing_data = self.get_existing_data(identifier, 'ISBN' if self.input_file_type.get() == 1 else 'OCN')


            # Determine what information is missing
            missing_data = [key for key, value in output_options.items() if value and key not in existing_data]

            # Fetch missing data based on priority list and update existing_data with new findings
            if missing_data:
                for source_name in self.priority_list:
                    source = self.source_mapping.get(source_name)
                    if source:
                        result = source.query(identifier)
                        # Update existing data with fetched information
                        for data_type in list(missing_data):  # Use list(missing_data) to safely modify missing_data while iterating
                            if data_type.lower() in result:
                                existing_data[data_type] = result[data_type.lower()]
                                missing_data.remove(data_type)  # Remove the found data type from missing_data
                                
                        # Break out of the loop if no more data is missing
                        if not missing_data:
                            break

            # Now that all sources have been queried, write the existing_data to the output file
            self.write_data_to_output_file(identifier, existing_data)

            # Simulate work
            time.sleep(1)
            
        self.after(0, self.stop_search)

    def stop_search(self):
        self.search_active = False
        self.toggle_ui_for_search(False)

        logging.info("Search stopped")
        messagebox.showinfo("Search", "Search stopped.")


    def toggle_ui_for_search(self, is_searching):
        if is_searching:
            # Hide the main UI elements
            self.top_frame.pack_forget()
            #self.button_frame.pack_forget()
            self.output_frame.pack_forget()
            self.start_button.pack_forget()
            self.open_log_button.pack_forget()
            self.choose_output_file_button.pack_forget()
            self.set_priority_button.pack_forget()
        
            # Make sure the stop button is visible and enabled
            self.stop_button.pack(side='left', padx=5)
            self.stop_button['state'] = 'normal'
            
            # Start showing animated "Searching..." message
            self.search_status_var.set("Searching...")
            self.search_status_label.pack(side='top', pady=(20, 0), expand=True)

            # Explicitly pack the stop button below the search status label
            self.stop_button['state'] = 'normal'  # Enable the button if it was disabled
            self.stop_button.pack(side='top', pady=(10, 0))
        else:
            # Stop animation and hide the search status label
            self.search_in_progress = False
            self.search_status_label.pack_forget()
            self.stop_button.pack_forget()  # Ensure stop button is also hidden when not searching

            # Restore UI elements to their initial state
            self.button_frame.pack_forget()
            self.setup_ui()

    def animate_search_status(self, initial_message):
        def update_message():
            dot_count = 0
            while self.search_in_progress:
                time.sleep(0.5)  # Time between updates
                self.search_status_var.set(f"{self.current_identifier}/{self.total_identifiers}\n{initial_message}{'.' * dot_count}")
                dot_count = (dot_count + 1) % 4  # Cycle through 0 to 3 dots
        self.search_in_progress = True
        threading.Thread(target=update_message, daemon=True).start()


    def choose_output_file(self):
        f = asksaveasfile(mode='w', defaultextension=".txt", filetypes=[("Text Documents", "*.txt"), ("All Files", "*.*")])
        if f is not None:  # asksaveasfile return `None` if dialog closed with "cancel".
            self.output_file_path = f.name
            messagebox.showinfo("Success", "Output file selected: " + self.output_file_path)
            f.close()  # `asksaveasfile` mode 'w' requires manual closure

    def set_priority(self):
        # Placeholder for setting priority, assuming PriorityListApp is correctly implemented
        priority_window = tk.Toplevel(self)
        PriorityListApp(priority_window, self.update_priority_list)

    def update_priority_list(self, updated_list):
        self.priority_list = updated_list
        logging.info(f"Updated priority list: {self.priority_list}")

    def open_log(self, log_path):
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
