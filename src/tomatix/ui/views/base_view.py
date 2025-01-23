import customtkinter as ctk
from datetime import datetime

class BaseView(ctk.CTkFrame):
    """Base class for all views with common functionality."""

    def __init__(self, parent, on_back=None, debug=False):
        super().__init__(parent)
        self.debug = debug
        self.on_back = on_back
        self._debug_log("__init__ called")

    def _debug_log(self, message):
        if self.debug:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            print(f"[DEBUG {self.__class__.__name__}] {now} - {message}")

    def _add_back_button(self):
        """Add back button if on_back callback is provided."""
        if self.on_back:
            ctk.CTkButton(
                self,
                text="Back",
                command=self.on_back,
                width=200
            ).pack(pady=(10, 0))

    def bind_keys(self, root):
        """Bind view-specific keyboard shortcuts."""
        pass

    def unbind_keys(self, root):
        """Unbind view-specific keyboard shortcuts."""
        pass