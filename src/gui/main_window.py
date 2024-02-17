import tkinter as tk
from tkinter import filedialog
from tkinter.filedialog import asksaveasfile
from tkinter import ttk
import sys
import os
import logging

from src.gui.priority_list import PriorityListApp

src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_dir not in sys.path:
    sys.path.append(src_dir)

# Now you can import file_processor from util
from src.util import file_processor

class LibraryMetadataHarvesterApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('Library Metadata Harvester')
        self.configure(bg='#333333')  # Set a dark background color
        self.geometry('600x500')  # Adjust the size

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

        # set searching priority
        self.set_priority = ttk.Button(self.input_frame, text="Set Searching Priority", command=self.set_priority)
        self.set_priority.grid(row=8, column=0, sticky='w', padx=(0, 5), pady=(5, 0))

        # buttons area
        self.button_frame = ttk.Frame(self, style='TFrame')
        self.button_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # start searching
        self.start_button = ttk.Button(self.button_frame, text="Start Search", command=self.start_search)
        self.start_button.pack(side='left',pady=10, padx=4)

        # stop searching
        self.stop_button = ttk.Button(self.button_frame, text="Stop Search", command=self.stop_search)
        self.stop_button.pack(side='left', pady=10, padx=8)

        #Open Log Button
        self.open_log_button = ttk.Button(self.button_frame, text="Open Detailed Log", command=lambda: self.open_log('../logs/example.log'))
        self.open_log_button.pack(side='left', pady=10, padx=4)

        # Export button
        self.export_button = ttk.Button(self.button_frame, text="Export Output File", command=self.export_data)
        self.export_button.pack(side='left', pady=10, padx=8)

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
        # Retrieve selected priorities

        # Generate a log
        self.generate_log('../logs/example.log')

        # Get the file path from the entry widget
        file_path = self.file_entry.get()

        # Process the file
        file_type, data = file_processor.read_and_validate_file(file_path)
        if file_type == 'Invalid':
             logging.info("Invalid file or file format.")
        else:
             logging.info(f"File contains valid {file_type} entries.")
            # Continue with the search logic using the data
             logging.info(str(self.get_current_options()))
        

    def stop_search(self):
        logging.info("Search stopped...")


    def set_priority(self):
        root = tk.Tk()
        app = PriorityListApp(root)
        root.mainloop()


    def generate_log(self, log_file_path):
        logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


    def open_log(self, log_path):
        # Create the Tkinter root widget
        root = tk.Tk()
        root.title("Log Viewer")

        # Create a text widget to display file content
        text = tk.Text(root, wrap="word")
        text.pack(expand=True, fill="both")
        if log_path:
            with open(log_path, 'r') as file:
                content = file.read()
                text.delete('1.0', tk.END)  # Clear previous content
                text.insert(tk.END, content)


    def export_data(self):
        f = asksaveasfile(initialfile='Untitled.txt', defaultextension=".txt", filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")])

if __name__ == "__main__":
    app = LibraryMetadataHarvesterApp()
    app.mainloop()
