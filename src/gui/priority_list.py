import tkinter as tk

class PriorityListApp:
    def __init__(self, master, callback):
        self.master = master
        self.callback = callback
        self.master.title("Priority List")

        self.entries = ["OCLC API", "Library of Congress API", "Harvard Library API", "Open Library API", "Google Books API", "Yale", "Columbia", "University of Virginia", "Stanford", "Johns Hopkins U", "Cornell", "NCSU", "Duke", "Penn State", "Indiana U", "McGill", "VOILA"]

        self.listbox = tk.Listbox(master, selectmode=tk.SINGLE)
        for entry in self.entries:
            self.listbox.insert(tk.END, entry)

        self.scrollbar = tk.Scrollbar(master, orient=tk.VERTICAL)
        self.scrollbar.config(command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        self.up_button = tk.Button(master, text="Move Up", command=self.move_up)
        self.down_button = tk.Button(master, text="Move Down", command=self.move_down)
        self.confirm = tk.Button(master, text="Confirm", command=self.confirm_and_exit)

        self.listbox.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        self.scrollbar.grid(row=0, column=1, padx=(0, 5), pady=5, sticky=tk.NS)
        self.up_button.grid(row=1, column=0, padx=5, pady=5)
        self.down_button.grid(row=1, column=1, padx=5, pady=5)
        self.confirm.grid(row=1, column=2, padx=5, pady=5)

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

    def confirm_and_exit(self):
        # Callback to update the priority list in the main app
        self.callback(list(self.listbox.get(0, tk.END)))
        self.master.destroy()


def main():
    root = tk.Tk()
    PriorityListApp(root, lambda: 1)
    root.mainloop()

if __name__ == "__main__":
    main()