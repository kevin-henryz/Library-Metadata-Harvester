import tkinter as tk

class PriorityList:
    def __init__(self, master, callback, selected_sources, unused_sources):
        self.master = master
        self.callback = callback
        self.selected_sources = selected_sources
        self.unused_sources = unused_sources
        self.master.title("Priority List")

        self.setup_widgets()
        self.populate_listboxes()

 


    def setup_widgets(self):
            
            self.label_left = tk.Label(self.master, text="Selected sources")
            self.label_right = tk.Label(self.master, text="Unused sources")
            self.listbox = tk.Listbox(self.master, selectmode=tk.SINGLE)
            self.listbox_right = tk.Listbox(self.master, selectmode=tk.SINGLE)
            self.scrollbar = tk.Scrollbar(self.master, orient=tk.VERTICAL)
            self.scrollbar.config(command=self.listbox.yview)
            self.listbox.config(yscrollcommand=self.scrollbar.set)
            self.scrollbar_right = tk.Scrollbar(self.master, orient=tk.VERTICAL)
            self.scrollbar_right.config(command=self.listbox_right.yview)
            self.listbox_right.config(yscrollcommand=self.scrollbar_right.set)
            self.up_button = tk.Button(self.master, text="Move Up", command=self.move_up)
            self.down_button = tk.Button(self.master, text="Move Down", command=self.move_down)
            self.remove_button = tk.Button(self.master, text="Remove", command=self.delete_item)
            self.add_button = tk.Button(self.master, text="  Add  ", command=self.add_item)
            self.confirm = tk.Button(self.master, text="Confirm", command=self.confirm_and_exit)

            #Layout
            self.label_left.grid(row=0, column=0, padx=20, pady=0, sticky="w")
            self.listbox.grid(row=1, column=0, padx=20, pady=5, sticky=tk.NSEW)
            self.scrollbar.grid(row=1, column=1, padx=(0, 5), pady=5, sticky=tk.NS)
            self.label_right.grid(row=0, column=2, padx=5, pady=0, sticky="w")
            self.listbox_right.grid(row=1, column=2, padx=2, pady=5, sticky=tk.NSEW)
            self.scrollbar_right.grid(row=1, column=3, padx=(0, 5), pady=5, sticky=tk.NS)
            self.up_button.grid(row=2, column=0, padx=20, pady=10, sticky="w")
            self.down_button.grid(row=2, column=0, padx=0, pady=10, sticky="e")
            self.remove_button.grid(row=2, column=2, padx=0, pady=10, sticky="w")
            self.add_button.grid(row=2, column=2, padx=5, pady=10, sticky="e")
            self.confirm.grid(row=2, column=3, padx=15, pady=10, sticky="w")


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

def main():
    root = tk.Tk()
    PriorityList(root, lambda: 1)
    root.mainloop()

if __name__ == "__main__":
    main()