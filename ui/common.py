import tkinter as tk


def confirm_modal(root, title: str, message: str) -> bool:
    """Show a modal Yes/Cancel dialog and return True if confirmed."""
    win = tk.Toplevel(root)
    win.title(title)
    win.resizable(False, False)
    win.transient(root)
    win.grab_set()
    frame = tk.Frame(win, padx=16, pady=12)
    frame.pack(fill="both", expand=True)
    tk.Label(frame, text=message, anchor="w", justify="left").pack(pady=(0, 8))
    btns = tk.Frame(frame)
    btns.pack(anchor="e")
    result = {"val": False}

    def do_yes(event=None):
        result["val"] = True
        win.destroy()

    def do_no(event=None):
        result["val"] = False
        win.destroy()

    yes_btn = tk.Button(btns, text="Yes", width=8, command=do_yes)
    no_btn = tk.Button(btns, text="Cancel", width=8, command=do_no)
    no_btn.pack(side="right")
    yes_btn.pack(side="right", padx=(0, 8))

    win.bind("<Return>", do_yes)
    win.bind("<Escape>", do_no)
    yes_btn.focus_set()
    root.wait_window(win)
    return result["val"]
