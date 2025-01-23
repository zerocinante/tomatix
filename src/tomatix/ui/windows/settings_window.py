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
        self.geometry("300x450")

        # Bind Escape key to close
        self.bind("<Escape>", lambda e: self.destroy())

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
        # Main container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(padx=20, pady=20, fill="both", expand=True)

        # Title
        ctk.CTkLabel(
            container,
            text="Timer Settings",
            font=("SF Pro Display", 24),
            text_color="#FFFFFF"
        ).pack(pady=(0, 30))

        # Settings frame
        settings_frame = ctk.CTkFrame(container, fg_color="transparent")
        settings_frame.pack(fill="x", pady=(0, 20))

        # Focus Round duration
        self._create_setting_group(
            settings_frame,
            "Focus Round",
            "minutes",
            self.timer_controller.timer.focus_round_duration // 60
        )

        # Recharge duration
        self._create_setting_group(
            settings_frame,
            "Recharge",
            "minutes",
            self.timer_controller.timer.recharge // 60
        )

        # Extended Recharge duration
        self._create_setting_group(
            settings_frame,
            "Extended Recharge",
            "minutes",
            self.timer_controller.timer.big_recharge // 60
        )

        # Error label (hidden by default)
        self.error_label = ctk.CTkLabel(
            container,
            text="Please enter valid numbers",
            text_color="#FF6B6B",
            font=("SF Pro Display", 14)
        )

        # Buttons frame
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        # Save button
        ctk.CTkButton(
            button_frame,
            text="Save Changes",
            command=self.save_settings,
            height=32,
            corner_radius=16,
            font=("SF Pro Display", 14)
        ).pack(fill="x")

        # Cancel button
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            height=32,
            corner_radius=16,
            font=("SF Pro Display", 14),
            fg_color="transparent",
            hover_color="#404040"
        ).pack(fill="x", pady=(10, 0))

    def _create_setting_group(self, parent, label_text, unit_text, default_value):
        """Create a grouped setting with label and entry."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 15))

        # Label
        ctk.CTkLabel(
            frame,
            text=label_text,
            font=("SF Pro Display", 16),
            text_color="#FFFFFF"
        ).pack(anchor="w")

        # Entry with unit label
        entry_frame = ctk.CTkFrame(frame, fg_color="transparent")
        entry_frame.pack(fill="x", pady=(5, 0))

        entry = ctk.CTkEntry(
            entry_frame,
            height=32,
            font=("SF Pro Display", 14),
            corner_radius=16
        )
        entry.pack(side="left", expand=True)
        entry.insert(0, str(default_value))

        ctk.CTkLabel(
            entry_frame,
            text=unit_text,
            font=("SF Pro Display", 14),
            text_color="#666666"
        ).pack(side="left", padx=(10, 0))

        # Store entry widget reference
        setattr(self, f"{label_text.lower().replace(' ', '_')}_entry", entry)

    def save_settings(self):
        """Save the new settings and close the window."""
        self._debug_log("save_settings called")
        try:
            focus = int(self.focus_round_entry.get()) * 60
            recharge = int(self.recharge_entry.get()) * 60
            big_recharge = int(self.extended_recharge_entry.get()) * 60

            self.timer_controller.save_settings(focus, recharge, big_recharge)
            self.destroy()
        except ValueError:
            self.error_label.pack(pady=(10, 0))