import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import sys
import os

src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if src_dir not in sys.path:
    sys.path.append(src_dir)

# Now you can import file_processor from util
from util import file_processor

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

        # Input Frame Widgets
        self.file_entry = ttk.Entry(self.input_frame, width=50)
        self.file_entry.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        self.browse_button = ttk.Button(self.input_frame, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=1, sticky='ew')

        self.start_button = ttk.Button(self.input_frame, text="Start Search", command=self.start_search)
        self.start_button.grid(row=1, column=0, sticky='ew', padx=(0, 5), pady=(5, 0))

        self.stop_button = ttk.Button(self.input_frame, text="Stop", command=self.stop_search)
        self.stop_button.grid(row=1, column=1, sticky='ew', pady=(5, 0))

        # OCN Key entry
        self.ocn_frame = ttk.Frame(self.input_frame, style='TFrame')
        self.ocn_frame.grid(row=2, columnspan=2, pady=20, padx=10, sticky='ew')

        self.ocn_label = ttk.Label(self.ocn_frame, text="OCN Key:", style='TLabel')
        self.ocn_label.pack(anchor='w')

        self.ocn_entry = ttk.Entry(self.ocn_frame, width=50)
        self.ocn_entry.pack(side='left', padx=(0, 5))

        self.enter_button = ttk.Button(self.ocn_frame, text="Enter", command=self.enter_ocn_key)
        self.enter_button.pack(side='left')
        
        # Right Side - Priority Frame
        self.priority_frame = ttk.Frame(self.top_frame, style='TFrame')
        self.priority_frame.pack(side='right', fill='x', expand=True)

        # Priority List
        ttk.Label(self.priority_frame, text="Set Source Priorities", style='TLabel').pack()

        self.sources = ["Source A", "Source B", "Source C"]
        self.priority_comboboxes = []

        for i in range(1, 4):
            ttk.Label(self.priority_frame, text=f"Priority {i}:", style='TLabel').pack(pady=(5, 0))
            priority_box = ttk.Combobox(self.priority_frame, values=self.sources, state="readonly")
            priority_box.pack()
            priority_box.set(self.sources[i-1])  # Set default value
            self.priority_comboboxes.append(priority_box)
        
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

    def get_priorities(self):
        """Retrieves the selected priorities from the comboboxes."""
        selected_priorities = [box.get() for box in self.priority_comboboxes]
        return selected_priorities    

    def start_search(self):
        # Retrieve selected priorities

        # Get the file path from the entry widget
        file_path = self.file_entry.get()

        # Process the file
        file_type, data = file_processor.read_and_validate_file(file_path)
        if file_type == 'Invalid':
            self.log_message("Invalid file or file format.")
        else:
            self.log_message(f"File contains valid {file_type} entries.")
            # Continue with the search logic using the data
            priorities = self.get_priorities()
            self.log_message("Search started with priorities: " + ", ".join(priorities))
        

    def stop_search(self):
        self.log_message("Search stopped...")

    def enter_ocn_key(self):
        self.log_message("OCN Key entered.")

    def export_data(self):
        self.log_message("Data exported successfully.")

    def log_message(self, message):
        self.log_text.insert(tk.END, message + '\n')
        self.log_text.see(tk.END)
        self.log_text.update_idletasks()

if __name__ == "__main__":
    app = LibraryMetadataHarvesterApp()
    app.mainloop()
