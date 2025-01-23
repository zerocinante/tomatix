import customtkinter as ctk
import webbrowser
from datetime import datetime

class SupportView(ctk.CTkFrame):
    """View for displaying support options (donations and feedback)."""

    def __init__(self, parent, on_back=None, debug=False):
        super().__init__(parent)
        self.debug = debug
        self.on_back = on_back
        self._debug_log("__init__ called")

        self._setup_ui()

    def _debug_log(self, message):
        if self.debug:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            print(f"[DEBUG {self.__class__.__name__}] {now} - {message}")

    def _setup_ui(self):
        """Create and arrange the UI elements."""
        # Title
        ctk.CTkLabel(
            self,
            text="Support Tomatix",
            font=("Helvetica", 24)
        ).pack(pady=(20, 10))

        # Description
        ctk.CTkLabel(
            self,
            text="If you find Tomatix helpful,\nconsider supporting its development!",
            font=("Helvetica", 16)
        ).pack(pady=(0, 20))

        # Donation button
        ctk.CTkButton(
            self,
            text="Buy Me a Coffee",
            command=self._open_donation_link,
            width=200
        ).pack(pady=(0, 10))

        # Feedback button
        ctk.CTkButton(
            self,
            text="Give Feedback",
            command=self._open_feedback_link,
            width=200
        ).pack(pady=(0, 10))

        # Back button
        if self.on_back:
            ctk.CTkButton(
                self,
                text="Back",
                command=self.on_back,
                width=200
            ).pack(pady=(10, 0))

    def _open_donation_link(self):
        """Open the donation link in the default browser."""
        self._debug_log("_open_donation_link called")
        webbrowser.open("https://buymeacoffee.com/zerocinante")

    def _open_feedback_link(self):
        """Open the feedback form in the default browser."""
        self._debug_log("_open_feedback_link called")
        webbrowser.open("https://forms.gle/ZcZjNw5ZXupr4Rug7")

    def bind_keys(self, root):
        """Bind view-specific keyboard shortcuts."""
        pass

    def unbind_keys(self, root):
        """Unbind view-specific keyboard shortcuts."""
        pass