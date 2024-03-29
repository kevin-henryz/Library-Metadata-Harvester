import tkinter as tk

class PriorityList:
    def __init__(self, master, callback, priorityList):
        self.master = master
        self.callback = callback
        self.master.title("Priority List")

        self.entries = priorityList
        self.entries_right = []

        self.label_left = tk.Label(master, text="Selected sources")
        self.label_right = tk.Label(master, text="Unused sources")
        self.listbox = tk.Listbox(master, selectmode=tk.SINGLE)
        for entry in self.entries:
            self.listbox.insert(tk.END, entry)

        self.listbox_right = tk.Listbox(master, selectmode=tk.SINGLE)
        for entry in self.entries_right:
            self.listbox_right.insert(tk.END, entry)

        self.scrollbar = tk.Scrollbar(master, orient=tk.VERTICAL)
        self.scrollbar.config(command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        self.scrollbar_right = tk.Scrollbar(master, orient=tk.VERTICAL)
        self.scrollbar_right.config(command=self.listbox_right.yview)
        self.listbox_right.config(yscrollcommand=self.scrollbar_right.set)

        self.up_button = tk.Button(master, text="Move Up", command=self.move_up)
        self.down_button = tk.Button(master, text="Move Down", command=self.move_down)
        self.remove_button = tk.Button(master, text=" Delete ", command=self.delete_item)
        self.add_button = tk.Button(master, text="  Add  ", command=self.add_item)
        self.confirm = tk.Button(master, text="Confirm", command=self.confirm_and_exit)

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

        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)

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
            self.entries.remove(item)
            self.entries_right.append(item)
            self.update_listboxes()

    def add_item(self):
        selected_index = self.listbox_right.curselection()
        if selected_index:
            item = self.listbox_right.get(selected_index)
            self.entries_right.remove(item)
            self.entries.append(item)
            self.update_listboxes()

    def confirm_and_exit(self):
        # Callback to update the priority list in the main app
        self.callback(list(self.listbox.get(0, tk.END)))
        self.master.destroy()

    def update_listboxes(self):
        self.listbox.delete(0, tk.END)
        for entry in self.entries:
            self.listbox.insert(tk.END, entry)
        self.listbox_right.delete(0, tk.END)
        for entry in self.entries_right:
            self.listbox_right.insert(tk.END, entry)


def main():
    root = tk.Tk()
    PriorityList(root, lambda: 1)
    root.mainloop()

if __name__ == "__main__":
    main()