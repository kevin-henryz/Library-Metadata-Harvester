import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import sys
import os

src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from util.file_processor import *
from db.database_manager import DatabaseManager


class LibraryMetadataHarvesterApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Library Metadata Harvester')
        self.configure(bg='#333333')  # Set a dark background color
        self.geometry('800x600')  # Adjust the size

        # Define the style for the dark theme
        self.style = ttk.Style(self)
        self.style.theme_use('clam')  # 'clam' theme allows for more color customization

        # Configure the colors for the widgets
        self.style.configure('TButton', background='#555555', foreground='white', borderwidth=1)
        self.style.configure('TFrame', background='#333333')
        self.style.configure('TCheckbutton', background='#333333', foreground='white')
        self.style.configure('TRadioButton', background='#333333', foreground='white')
        self.style.configure('TLabel', background='#333333', foreground='white')
        self.style.configure('TEntry', background='#555555', foreground='white', fieldbackground='#555555', borderwidth=1)
        self.style.map('TEntry', fieldbackground=[('focus', '#555555')], foreground=[('focus', 'white')])

        # Define main UI components
        self.setup_ui()

        # Initialize DatabaseManager
        self.db_manager = DatabaseManager()
        self.db_manager.create_table("book_data", "Isbn INTEGER PRIMARY KEY, Ocn INTEGER, Lccn TEXT, Source TEXT, Doi TEXT")

    def setup_ui(self):
        # Container for Input and Priority Frames
        self.top_frame = ttk.Frame(self, style='TFrame')
        self.top_frame.pack(side='top', fill='x', expand=True, padx=10, pady=10)

        # Left Side - Input Frame
        self.input_frame = ttk.Frame(self.top_frame, style='TFrame')
        self.input_frame.pack(side='left', fill='x', expand=True)

        # Data Type of Input File
        self.lable_input_file_type = ttk.Label(self.input_frame, text="Data Type of Input File:", style='TLabel')
        self.lable_input_file_type.grid(row=0, column=0, sticky='w',)

        self.input_file_type = tk.IntVar()

        self.rdb_input_file_type_isbn = ttk.Radiobutton(self.input_frame, text="ISBN", style='TRadiobutton', variable=self.input_file_type, value=1)
        self.rdb_input_file_type_isbn.grid(row=1, column=0, sticky='w', padx=(0, 5), pady=(5, 0))

        self.rdb_input_file_type_ocn = ttk.Radiobutton(self.input_frame, text="OCN", style='TRadiobutton', variable=self.input_file_type, value=0)
        self.rdb_input_file_type_ocn.grid(row=1, column=0, sticky='e', padx=(0, 5), pady=(5, 0))

        # Input Frame Widgets
        self.lable_browse_file = ttk.Label(self.input_frame, text="Browse Input File:", style='TLabel')
        self.lable_browse_file.grid(row=2, column=0, sticky='w', padx=(0, 5), pady=(30, 0))

        self.file_entry = ttk.Entry(self.input_frame, font=(35, 20))
        self.file_entry.grid(row=3, column=0, sticky='w', padx=(0, 5))

        self.browse_button = ttk.Button(self.input_frame, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=3, column=1)

        # Values included in output file
        self.output_value_isbn = tk.BooleanVar()
        self.output_value_ocn = tk.BooleanVar()
        self.output_value_lccn = tk.BooleanVar()
        self.output_value_lccn_source = tk.BooleanVar()
        self.output_value_doi = tk.BooleanVar()

        self.label_output_file_values = ttk.Label(self.input_frame, text="Values included in output file:", style='TLabel')
        self.label_output_file_values.grid(row=4, column=0, sticky='w',  padx=(0, 5), pady=(30, 0))

        self.checkbutton_output_value_isbn = ttk.Checkbutton(self.input_frame, text="ISBN", style='TCheckbutton', variable=self.output_value_isbn, onvalue=True, offvalue=False)
        self.checkbutton_output_value_isbn.grid(row=5, column=0, sticky='w', padx=(0, 5), pady=(5, 0))

        self.checkbutton_output_value_ocn = ttk.Checkbutton(self.input_frame, text="OCN ", style='TCheckbutton', variable=self.output_value_ocn, onvalue=True, offvalue=False)
        self.checkbutton_output_value_ocn.grid(row=5, column=0, padx=(0, 72), pady=(5, 0))

        self.checkbutton_output_value_lccn = ttk.Checkbutton(self.input_frame, text="LCCN", style='TCheckbutton', variable=self.output_value_lccn, onvalue=True, offvalue=False)
        self.checkbutton_output_value_lccn.grid(row=6, column=0, sticky='w', padx=(0, 5), pady=(5, 0))

        self.checkbutton_output_value_lccn_source = ttk.Checkbutton(self.input_frame, text="LCCN_source", style='TCheckbutton', variable=self.output_value_lccn_source, onvalue=True, offvalue=False)
        self.checkbutton_output_value_lccn_source.grid(row=6, column=0, padx=(0, 20), pady=(5, 0))

        self.checkbutton_output_value_doi = ttk.Checkbutton(self.input_frame, text="DOI", style='TCheckbutton', variable=self.output_value_doi, onvalue=True, offvalue=False)
        self.checkbutton_output_value_doi.grid(row=7, column=0, sticky='w', padx=(0, 5), pady=(5, 0))

        self.start_button = ttk.Button(self.input_frame, text="Start Search", command=self.start_search)
        self.start_button.grid(row=8, column=0, sticky='w', padx=(0, 5), pady=(15, 0))

        self.stop_button = ttk.Button(self.input_frame, text="Stop Search", command=self.stop_search)
        self.stop_button.grid(row=8, column=0, padx=(170, 0), pady=(15, 0))
        
        # Log area
        self.log_frame = ttk.Frame(self, style='TFrame')
        self.log_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.log_label = ttk.Label(self.log_frame, text="Logs:", style='TLabel')
        self.log_label.pack(anchor='nw', padx=5, pady=(0, 5))

        self.log_text = tk.Text(self.log_frame, height=10, bg='#222222', fg='white', borderwidth=1)
        self.log_text.pack(fill='both', expand=True)

        # Export button
        self.export_button = ttk.Button(self, text="Export Metadata", command=self.export_data)
        self.export_button.pack(side='bottom', pady=10, padx=10)

    def browse_file(self):
        filename = filedialog.askopenfilename()
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, filename)


    def get_current_options(self):
        """Retrieve and return the current selected options in the UI."""
        options = {
            'input_file_type': 'ISBN' if self.input_file_type.get() == 1 else 'OCN',
            'output_values': {
                'isbn': self.output_value_isbn.get(),
                'ocn': self.output_value_ocn.get(),
                'lccn': self.output_value_lccn.get(),
                'lccn_source': self.output_value_lccn_source.get(),
                'doi': self.output_value_doi.get()
            }
        }
        return options    

    def start_search(self):
        
        # Retrieve selected priorities and get the file path from the entry widget
        file_path = self.file_entry.get()
        options = self.get_current_options()
        file_type = 'ISBN' if options['input_file_type'] == 'ISBN' else 'OCN'

        # Process the file
        # Assuming file_processor.read_and_validate_file returns a list of ISBNs/OCNs
        identifiers = read_and_validate_file(file_path)
        if not identifiers:
            self.log_message("Invalid file or file format.")
            return

        self.log_message(f"File contains valid {file_type} entries.")
        
        # Check each identifier in the database and process accordingly
        for identifier in identifiers:
            if self.db_manager.data_exists("book_data", f"Isbn = {identifier}" if file_type == 'ISBN' else f"Ocn = {identifier}"):
                self.log_message(f"Data for {identifier} already exists in the database.")
                # Fetch and process data from the database if necessary
            else:
                self.log_message(f"Fetching data for {identifier} from external sources.")
                # Fetch data from API and insert it into the database
                # Example: metadata = fetch_metadata_from_api(identifier)
                # self.db_manager.insert_data("book_data", (identifier, metadata['Ocn'], metadata['Lccn'], ...))

        self.log_message("Search completed.")
        

    def stop_search(self):
        self.log_message("Search stopped...")

    def export_data(self):
        self.log_message("Data exported successfully.")

    def log_message(self, message):
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.update_idletasks()


if __name__ == "__main__":
    app = LibraryMetadataHarvesterApp()
    app.mainloop()
