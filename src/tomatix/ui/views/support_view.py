import customtkinter as ctk
import webbrowser
from datetime import datetime
from tomatix.ui.views.base_view import BaseView

class SupportView(BaseView):
    """View for displaying support options (donations and feedback)."""

    def __init__(self, parent, on_back=None, debug=False):
        super().__init__(parent, on_back, debug)
        self._setup_ui()

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

        # Add back button from base class
        self._add_back_button()

    def _open_donation_link(self):
        """Open the donation link in the default browser."""
        self._debug_log("_open_donation_link called")
        webbrowser.open("https://buymeacoffee.com/zerocinante")

    def _open_feedback_link(self):
        """Open the feedback form in the default browser."""
        self._debug_log("_open_feedback_link called")
        webbrowser.open("https://forms.gle/ZcZjNw5ZXupr4Rug7")