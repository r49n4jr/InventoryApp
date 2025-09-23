import tkinter as tk

class AutocompleteEntry(tk.Entry):
    def __init__(self, suggestions_callback, on_select_callback, qty_entry, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.suggestions_callback = suggestions_callback
        self.on_select_callback = on_select_callback
        self.qty_entry = qty_entry
        self.dropdown = None
        self.listbox = None
        self.matches = []
        self.selected_index = 0

        self.bind("<KeyRelease>", self.update_suggestions)
        self.bind("<Down>", self.move_down)
        self.bind("<Up>", self.move_up)
        self.bind("<Return>", self.select_item)

    def update_suggestions(self, event=None):
        if event and event.keysym in ["Up", "Down", "Return"]:
            return
        typed = self.get().lower()
        if typed == "":
            self.hide_dropdown()
            return
        self.matches = self.suggestions_callback(typed)
        if not self.matches:
            self.hide_dropdown()
            return
        if not self.dropdown:
            self.dropdown = tk.Toplevel(self)
            self.dropdown.wm_overrideredirect(True)
            self.dropdown.attributes("-topmost", True)
            self.listbox = tk.Listbox(self.dropdown, height=8)
            self.listbox.pack(side="left", fill="both", expand=True)
            scrollbar = tk.Scrollbar(self.dropdown, orient="vertical", command=self.listbox.yview)
            scrollbar.pack(side="right", fill="y")
            self.listbox.config(yscrollcommand=scrollbar.set)
        self.listbox.delete(0, tk.END)
        for match in self.matches:
            self.listbox.insert(tk.END, match)
        self.selected_index = 0
        self.update_selection()
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.dropdown.geometry(f"{self.winfo_width()}x160+{x}+{y}")
        self.dropdown.deiconify()

    def update_selection(self):
        self.listbox.select_clear(0, tk.END)
        self.listbox.select_set(self.selected_index)
        self.listbox.activate(self.selected_index)

    def move_down(self, event):
        if self.listbox and self.selected_index < len(self.matches) - 1:
            self.selected_index += 1
            self.update_selection()
        return "break"

    def move_up(self, event):
        if self.listbox and self.selected_index > 0:
            self.selected_index -= 1
            self.update_selection()
        return "break"

    def select_item(self, event=None):
        if self.listbox and self.matches:
            selected = self.matches[self.selected_index]
            self.delete(0, tk.END)
            self.insert(0, selected)
            self.hide_dropdown()
            self.on_select_callback(selected)
            self.qty_entry.focus()
            self.qty_entry.select_range(0, tk.END)
            return "break"

    def hide_dropdown(self):
        if self.dropdown:
            self.dropdown.withdraw()
