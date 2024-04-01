import tkinter as tk

class PriorityList:
    def __init__(self, master, callback, selected_sources, unused_sources,window_attributes):
        self.master = master
        self.callback = callback
        self.selected_sources = selected_sources
        self.unused_sources = unused_sources
        self.master.title("Priority List")

        self.set_size_and_position(window_attributes)

        self.setup_widgets()
        self.populate_listboxes()

    def set_size_and_position(self, window_attributes):
        # Decrease the width and height by a percentage or fixed value as needed
        width = int(window_attributes['width'] * 0.80)  # Decrease width by 10%
        height = int(window_attributes['height'] * 0.95)  # Decrease height by 10%

        # Offset to the left by decreasing the 'x' position
        # Adjust the offset value as needed
        offset = 50  # Offset 50 pixels to the left
        x = window_attributes['x'] - offset
        
        # Use the same 'y' position
        y = window_attributes['y'] - offset

        self.master.geometry(f"{width}x{height}+{x}+{y}")

 
    def setup_widgets(self):
        # Setup grid options for uniformity and alignment
        grid_options = {'padx': 5, 'pady': 5, 'sticky': tk.NSEW}
        button_frame_options = {'padx': 10, 'pady': 10}  # Padding options for the buttons' frame

        # Configure the master grid
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(2, weight=1)
        self.master.grid_rowconfigure(1, weight=1)

        # Labels
        self.label_left = tk.Label(self.master, text="Selected Sources")
        self.label_right = tk.Label(self.master, text="Unused Sources")
        self.label_left.grid(row=0, column=0, **grid_options)
        self.label_right.grid(row=0, column=2, **grid_options)
        
        # Listboxes and Scrollbars
        self.listbox = tk.Listbox(self.master, selectmode=tk.SINGLE)
        self.scrollbar = tk.Scrollbar(self.master, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.listbox.grid(row=1, column=0, **grid_options)
        self.scrollbar.grid(row=1, column=1, sticky=tk.NS + tk.E)
        
        self.listbox_right = tk.Listbox(self.master, selectmode=tk.SINGLE)
        self.scrollbar_right = tk.Scrollbar(self.master, orient=tk.VERTICAL, command=self.listbox_right.yview)
        self.listbox_right.config(yscrollcommand=self.scrollbar_right.set)
        self.listbox_right.grid(row=1, column=2, **grid_options)
        self.scrollbar_right.grid(row=1, column=3, sticky=tk.NS + tk.E)

        # Buttons Frame
        self.buttons_frame = tk.Frame(self.master)
        self.buttons_frame.grid(row=2, column=0, columnspan=4, **button_frame_options)
        
        # Buttons
        self.up_button = tk.Button(self.buttons_frame, text="Move Up", command=self.move_up)
        self.down_button = tk.Button(self.buttons_frame, text="Move Down", command=self.move_down)
        self.remove_button = tk.Button(self.buttons_frame, text="Remove", command=self.delete_item)
        self.add_button = tk.Button(self.buttons_frame, text="Add", command=self.add_item)
        self.confirm_button = tk.Button(self.buttons_frame, text="Confirm", command=self.confirm_and_exit)

        # Place buttons within the frame
        self.up_button.pack(side=tk.LEFT, padx=5)
        self.down_button.pack(side=tk.LEFT, padx=5)
        self.remove_button.pack(side=tk.LEFT, padx=5)  
        self.add_button.pack(side=tk.LEFT, padx=5)
        self.confirm_button.pack(side=tk.RIGHT, padx=5)  # Align confirm to the right for distinction




    def populate_listboxes(self):
        for entry in self.selected_sources:
            self.listbox.insert(tk.END, entry)
        for entry in self.unused_sources:
            self.listbox_right.insert(tk.END, entry)
    



    def move_up(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_index = int(selected_index[0])
            if selected_index > 0:
                item = self.listbox.get(selected_index)
                self.listbox.delete(selected_index)
                self.listbox.insert(selected_index - 1, item)
                self.listbox.selection_set(selected_index - 1)

    def move_down(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_index = int(selected_index[0])
            if selected_index < self.listbox.size() - 1:
                item = self.listbox.get(selected_index)
                self.listbox.delete(selected_index)
                self.listbox.insert(selected_index + 1, item)
                self.listbox.selection_set(selected_index + 1)

    def delete_item(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            item = self.listbox.get(selected_index)
            self.listbox.delete(selected_index)
            self.listbox_right.insert(tk.END, item)

    def add_item(self):
        selected_index = self.listbox_right.curselection()
        if selected_index:
            item = self.listbox_right.get(selected_index)
            self.listbox_right.delete(selected_index)
            self.listbox.insert(tk.END, item)

    def confirm_and_exit(self):
        # Callback to update the priority list in the main app
        self.selected_sources = list(self.listbox.get(0, tk.END))
        self.unused_sources = list(self.listbox_right.get(0, tk.END))
        self.callback(self.selected_sources, self.unused_sources)
        self.master.destroy()

