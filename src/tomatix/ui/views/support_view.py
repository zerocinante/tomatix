import customtkinter as ctk
import webbrowser
from tomatix.ui.views.base_view import BaseView

class SupportView(BaseView):
    """A minimalist view for support options."""

    def __init__(self, parent, on_back=None, debug=False):
        super().__init__(parent, on_back, debug)
        self._setup_ui()

    def _setup_ui(self):
        """Create and arrange the UI elements."""
        # Center content frame
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(padx=10, pady=10, expand=True)

        # Support title
        ctk.CTkLabel(
            content,
            text="Support Tomatix",
            font=("SF Pro Display", 24),
            text_color="#FFFFFF"
        ).pack(pady=(0, 20))

        # Description
        ctk.CTkLabel(
            content,
            text="If you find Tomatix helpful,\nconsider supporting its development!",
            font=("SF Pro Display", 16),
            text_color="#666666"
        ).pack(pady=(0, 30))

        # Button frame
        button_frame = ctk.CTkFrame(content, fg_color="transparent")
        button_frame.pack(pady=(0, 30))

        # Support buttons
        ctk.CTkButton(
            button_frame,
            text="Buy Me a Coffee ☕",
            command=self._open_donation_link,
            width=200,
            height=32,
            corner_radius=16,
            font=("SF Pro Display", 14)
        ).pack(pady=(0, 10))

        ctk.CTkButton(
            button_frame,
            text="Give Feedback 💭",
            command=self._open_feedback_link,
            width=200,
            height=32,
            corner_radius=16,
            font=("SF Pro Display", 14)
        ).pack(pady=(0, 10))

        # Back button at the bottom
        ctk.CTkButton(
            self,
            text="Back to Focus",
            command=self.on_back,
            width=200,
            height=32,
            corner_radius=16,
            font=("SF Pro Display", 14)
        ).pack(pady=(0, 20))

    def _open_donation_link(self):
        """Open the donation link in the default browser."""
        self._debug_log("_open_donation_link called")
        webbrowser.open("https://buymeacoffee.com/zerocinante")

    def _open_feedback_link(self):
        """Open the feedback form in the default browser."""
        self._debug_log("_open_feedback_link called")
        webbrowser.open("https://forms.gle/ZcZjNw5ZXupr4Rug7")