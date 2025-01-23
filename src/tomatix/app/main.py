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

    # Create the main UI
    app = MainUI(root, debug=debug)

    if debug:
        print("[DEBUG] main: entering mainloop")
    root.mainloop()

if __name__ == "__main__":
    main(debug=False)
