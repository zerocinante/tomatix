import customtkinter as ctk
from datetime import datetime
import threading
import importlib.resources
from playsound import playsound

class AlertWindow(ctk.CTkToplevel):
    """Fullscreen alert window shown when a timer cycle completes."""

    def __init__(self, parent, message, on_close=None, debug=False):
        super().__init__(parent)
        self.debug = debug
        self.on_close = on_close
        self.message = message
        self._debug_log("__init__ called")

        # Play notification sound
        self._play_notification()

        # Wait for the window to be ready before configuring it
        self.after(10, self._initialize_window)

    def _initialize_window(self):
        """Initialize window after it's fully created."""
        self._debug_log("_initialize_window called")

        self.title("Timer Complete")
        self._make_fullscreen()
        self._setup_ui(self.message)

        # Make window modal
        self.transient(self.master)
        self.grab_set()

        # Bind key to close
        self.bind("<Escape>", lambda e: self.close())
        self.bind("<Return>", lambda e: self.close())
        self.bind("<space>", lambda e: self.close())

        self.after(30000, self.close)

    def _debug_log(self, message):
        if self.debug:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            print(f"[DEBUG {self.__class__.__name__}] {now} - {message}")

    def _play_notification(self):
        """Play the notification sound in a separate thread."""
        try:
            with importlib.resources.files('tomatix.resources').joinpath('notification.wav') as sound_path:
                if sound_path.exists():
                    threading.Thread(
                        target=lambda: playsound(str(sound_path)),
                        daemon=True
                    ).start()
        except Exception as e:
            self._debug_log(f"Error playing sound: {e}")

    def _make_fullscreen(self):
        """Make the window cover the full screen."""
        # Force window to top level and make it fullscreen
        self.lift()
        self.attributes('-topmost', True)
        self.attributes('-fullscreen', True)

    def _setup_ui(self, message):
        """Create and arrange the UI elements."""
        # Center the content
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create a frame for the content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=0, column=0, sticky="nsew")

        # Make the content frame center its contents vertically
        content.grid_rowconfigure(0, weight=1)
        content.grid_rowconfigure(2, weight=1)
        content.grid_columnconfigure(0, weight=1)

        message_label = ctk.CTkLabel(
            content,
            text=message,
            font=("Helvetica", 36),
            text_color="white",
        )
        message_label.grid(row=1, column=0, pady=(0, 40))

        # Close button
        close_button = ctk.CTkButton(
            content,
            text="Continue",
            command=self.close,
            width=200
        )
        close_button.grid(row=2, column=0, pady=(0, 0))

    def close(self, event=None):
        """Close the alert window."""
        self._debug_log("close called")
        if self.on_close:
            self.on_close("Focus")
        self.destroy()