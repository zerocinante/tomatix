import customtkinter as ctk
from datetime import datetime

class BaseView(ctk.CTkFrame):
    """Base class for all views with common functionality."""

    def __init__(self, parent, on_back=None, debug=False):
        super().__init__(parent)
        self.debug = debug
        self.on_back = on_back
        self._debug_log("__init__ called")

        # Add bottom padding frame
        self.bottom_padding = ctk.CTkFrame(self, fg_color="transparent", height=20)
        self.bottom_padding.pack(side="bottom", fill="x")
        self.bottom_padding.pack_propagate(False)

        # Bind to configure event to handle resizing
        self.bind("<Configure>", self._on_configure)

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

    def _on_configure(self, event):
        """Handle resize events by updating window size."""
        if event.widget == self:
            # Get the required size for all widgets
            required_width = self.winfo_reqwidth()
            required_height = self.winfo_reqheight()

            # Add some padding
            width = required_width + 20
            height = required_height + 20

            # Update window geometry if needed
            current_width = self.winfo_width()
            current_height = self.winfo_height()

            if width != current_width or height != current_height:
                self.master.geometry(f"{width}x{height}")