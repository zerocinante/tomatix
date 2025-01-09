# src/tomatix/app/main.py
import customtkinter as ctk
from tomatix.ui.main_ui import MainUI

def main(debug=False):
    """
    Initialize the CustomTkinter environment and launch the main Tomatix UI.
    We separate this from the UI class so that future entry points
    (e.g., CLI or web) can reuse the same UI logic if needed.
    """
    if debug:
        print("[DEBUG] main: starting application")

    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Tomatix Timer")
    root.geometry("300x300")

    # Create the main UI (which also creates and owns the TimerController)
    app = MainUI(root, debug=debug)

    # Set initial sizing and allow resizing
    root.update_idletasks()
    root.minsize(root.winfo_width(), root.winfo_height())
    root.resizable(True, True)

    if debug:
        print("[DEBUG] main: entering mainloop")
    root.mainloop()

if __name__ == "__main__":
    main(debug=False)
