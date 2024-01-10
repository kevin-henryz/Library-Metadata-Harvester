import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

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

        # Define main UI components based on the sketch
        self.setup_ui()

    def setup_ui(self):
        # Input File frame
        self.input_frame = ttk.Frame(self, style='TFrame')
        self.input_frame.pack(pady=20, fill='x', padx=10)

        self.file_entry = ttk.Entry(self.input_frame, width=50)
        self.file_entry.grid(row=0, column=0, sticky='ew', padx=(0, 5))

        self.browse_button = ttk.Button(self.input_frame, text="Browse", command=self.browse_file)
        self.browse_button.grid(row=0, column=1, sticky='ew')

        self.start_button = ttk.Button(self.input_frame, text="Start Search", command=self.start_search)
        self.start_button.grid(row=1, column=0, sticky='ew', padx=(0, 5), pady=(5, 0))

        self.stop_button = ttk.Button(self.input_frame, text="Stop", command=self.stop_search)
        self.stop_button.grid(row=1, column=1, sticky='ew', pady=(5, 0))

        # OCN Key entry
        self.ocn_frame = ttk.Frame(self, style='TFrame')
        self.ocn_frame.pack(pady=20, padx=10, anchor='w')

        self.ocn_label = ttk.Label(self.ocn_frame, text="OCN Key:", style='TLabel')
        self.ocn_label.pack(anchor='w')

        self.ocn_entry = ttk.Entry(self.ocn_frame, width=50)
        self.ocn_entry.pack(side='left', padx=(0, 5))

        self.enter_button = ttk.Button(self.ocn_frame, text="Enter", command=self.enter_ocn_key)
        self.enter_button.pack(side='left')

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

    def start_search(self):
        # Start search functionality
        self.log_message("File 'example.txt' loaded.")
        self.log_message("Search started...")

    def stop_search(self):
        # Stop search functionality
        self.log_message("Search stopped...")

    def enter_ocn_key(self):
        # Enter OCN key functionality
        self.log_message("OCN Key invalid: Try again...")

    def export_data(self):
        # Export data functionality
        self.log_message("Data exported succesfully...")

    def log_message(self, message):
        # Insert the message at the end of the Text widget
        self.log_text.insert(tk.END, message + '\n')
        # Ensure the latest message is visible
        self.log_text.see(tk.END)
        # Update the Text widget to refresh the display
        self.log_text.update_idletasks()

if __name__ == "__main__":
    app = LibraryMetadataHarvesterApp()
    app.mainloop()
