import customtkinter as ctk
from datetime import datetime

class SettingsWindow(ctk.CTkToplevel):
    """Configuration window for timer durations."""

    def __init__(self, parent, timer_controller, debug=False):
        super().__init__(parent)
        self.debug = debug
        self.timer_controller = timer_controller
        self._debug_log("__init__ called")

        self.title("Settings")
        self.geometry("300x400")

        self._setup_ui()

        # Make window modal
        self.transient(parent)
        self.grab_set()

    def _debug_log(self, message):
        if self.debug:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            print(f"[DEBUG {self.__class__.__name__}] {now} - {message}")

    def _setup_ui(self):
        """Create and arrange the UI elements."""
        # Focus Round duration
        ctk.CTkLabel(self, text="Focus Round (minutes)").pack(pady=(20, 0))
        self.focus_entry = ctk.CTkEntry(self)
        self.focus_entry.pack(pady=(5, 10))
        self.focus_entry.insert(0, str(self.timer_controller.timer.focus_round_duration // 60))

        # Recharge duration
        ctk.CTkLabel(self, text="Recharge (minutes)").pack(pady=(10, 0))
        self.recharge_entry = ctk.CTkEntry(self)
        self.recharge_entry.pack(pady=(5, 10))
        self.recharge_entry.insert(0, str(self.timer_controller.timer.recharge // 60))

        # Extended Recharge duration
        ctk.CTkLabel(self, text="Extended Recharge (minutes)").pack(pady=(10, 0))
        self.big_recharge_entry = ctk.CTkEntry(self)
        self.big_recharge_entry.pack(pady=(5, 10))
        self.big_recharge_entry.insert(0, str(self.timer_controller.timer.big_recharge // 60))

        # Save button
        ctk.CTkButton(
            self,
            text="Save",
            command=self.save_settings
        ).pack(pady=(20, 0))

    def save_settings(self):
        """Save the new settings and close the window."""
        self._debug_log("save_settings called")
        try:
            focus = int(self.focus_entry.get()) * 60
            recharge = int(self.recharge_entry.get()) * 60
            big_recharge = int(self.big_recharge_entry.get()) * 60

            self.timer_controller.save_settings(focus, recharge, big_recharge)
            self.destroy()
        except ValueError:
            # Show error if inputs aren't valid numbers
            ctk.CTkLabel(
                self,
                text="Please enter valid numbers",
                text_color="red"
            ).pack(pady=(10, 0))