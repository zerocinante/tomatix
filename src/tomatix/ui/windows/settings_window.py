import customtkinter as ctk
from datetime import datetime

class SettingsWindow(ctk.CTkToplevel):
    """Configuration window for timer durations."""

    # Maximum allowed values in minutes
    MAX_FOCUS_MINUTES = 480     # 8 hours
    MAX_RECHARGE_MINUTES = 120  # 2 hours
    MAX_BIG_RECHARGE_MINUTES = 240  # 4 hours
    MAX_CYCLES = 10  # Maximum number of focus rounds before extended recharge

    def __init__(self, parent, timer_controller, colors=None, debug=False):
        super().__init__(parent)
        self.debug = debug
        self.timer_controller = timer_controller
        self.colors = colors or {  # Fallback colors if none provided
            "primary": "#FF7F50",
            "secondary": "#95A5A6",
            "background": "#2B2B2B",
            "text": "#FFFFFF",
            "success": "#2ECC71",
            "warning": "#F39C12",
            "accent": "#E67E22"
        }
        self._debug_log("__init__ called")

        self.title("Settings")
        self.geometry("300x600")  # Increased height to fit all content

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

    def _calculate_flow_score(self, focus_mins, recharge_mins, big_recharge_mins, cycles):
        """
        Calculate normalized flow score based on work-to-rest ratio.
        Returns tuple of (score, total_work_mins, total_rest_mins)
        """
        try:
            # Convert all inputs to integers
            focus_mins = int(focus_mins)
            recharge_mins = int(recharge_mins)
            big_recharge_mins = int(big_recharge_mins)
            cycles = int(cycles)

            # Calculate total work and rest minutes
            total_work_mins = focus_mins * cycles
            total_rest_mins = (recharge_mins * (cycles - 1)) + big_recharge_mins

            # Calculate ratio (work:rest)
            current_ratio = total_work_mins / total_rest_mins

            # Calculate baseline ratio (25/5/15/4 pattern)
            baseline_work = 25 * 4  # 100 minutes of work
            baseline_rest = (5 * 3) + 15  # 30 minutes of rest
            baseline_ratio = baseline_work / baseline_rest

            # Normalize the score (1.0 = baseline ratio)
            score = round(current_ratio / baseline_ratio, 2)

            return score, total_work_mins, total_rest_mins
        except (ValueError, ZeroDivisionError):
            return None, 0, 0

    def _update_ratio_label(self, *args):
        """Update the flow score label whenever settings change."""
        try:
            focus = int(self.focus_round_entry.get())
            recharge = int(self.recharge_entry.get())
            big_recharge = int(self.extended_recharge_entry.get())
            cycles = int(self.cycles_entry.get())

            score, work_mins, rest_mins = self._calculate_flow_score(
                focus, recharge, big_recharge, cycles
            )

            if score:
                description = (
                    "more focus-intensive" if score > 1 else
                    "more rest-oriented" if score < 1 else
                    "balanced"
                )

                self.ratio_label.configure(
                    text=f"Flow Score: {score:.2f} ({description})"
                )
                self.ratio_label.pack()
            else:
                self.ratio_label.pack_forget()

        except ValueError:
            self.ratio_label.pack_forget()

    def _setup_ui(self):
        """Create and arrange the UI elements."""
        # Main container with padding
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(padx=20, pady=20, fill="both", expand=True)

        # Title
        ctk.CTkLabel(
            container,
            text="Timer Settings",
            font=("SF Pro Display", 24),
            text_color="#FFFFFF"
        ).pack(pady=(0, 5))  # Reduced bottom padding

        # Flow score label right below title
        self.ratio_label = ctk.CTkLabel(
            container,
            text="",
            font=("SF Pro Display", 12),
            text_color=self.colors["secondary"]
        )
        self.ratio_label.pack(pady=(0, 20))  # Added padding below score

        # Settings frame
        settings_frame = ctk.CTkFrame(container, fg_color="transparent")
        settings_frame.pack(fill="x", pady=(0, 10))

        # Create settings groups
        self._create_setting_group(
            settings_frame,
            "Focus Round",
            "minutes",
            self.timer_controller.timer.focus_round_duration // 60
        )

        self._create_setting_group(
            settings_frame,
            "Recharge",
            "minutes",
            self.timer_controller.timer.recharge // 60
        )

        self._create_setting_group(
            settings_frame,
            "Extended Recharge",
            "minutes",
            self.timer_controller.timer.big_recharge // 60
        )

        self._create_setting_group(
            settings_frame,
            "Cycles",
            "rounds",
            self.timer_controller.timer.cycles
        )

        # Bind entry changes to update ratio
        for entry_name in ['focus_round_entry', 'recharge_entry', 'extended_recharge_entry', 'cycles_entry']:
            entry = getattr(self, entry_name)
            entry.bind('<KeyRelease>', self._update_ratio_label)

        # Initial ratio calculation
        self._update_ratio_label()

        # Error label
        self.error_label = ctk.CTkLabel(
            container,
            text="",
            text_color="#FF6B6B",
            font=("SF Pro Display", 12),
            wraplength=260
        )
        self.error_label.pack(pady=(0, 10))
        self.error_label.pack_forget()

        # Buttons frame
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 0))

        # Save button
        ctk.CTkButton(
            button_frame,
            text="Save Changes",
            command=self.save_settings,
            height=32,
            corner_radius=16,
            font=("SF Pro Display", 14),
            fg_color=self.colors["primary"],
            hover_color=self.colors["accent"],
            text_color=self.colors["text"]
        ).pack(fill="x", pady=(0, 10))

        # Cancel button
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.destroy,
            height=32,
            corner_radius=16,
            font=("SF Pro Display", 14),
            fg_color="transparent",
            hover_color=self.colors["accent"],
            text_color=self.colors["text"]
        ).pack(fill="x")

    def _create_setting_group(self, parent, label_text, unit_text, default_value):
        """Create a grouped setting with label and entry."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=(0, 15))

        # Add max value to label
        max_value = {
            "Focus Round": self.MAX_FOCUS_MINUTES,
            "Recharge": self.MAX_RECHARGE_MINUTES,
            "Extended Recharge": self.MAX_BIG_RECHARGE_MINUTES,
            "Cycles": self.MAX_CYCLES
        }[label_text]

        # Label with max value hint
        ctk.CTkLabel(
            frame,
            text=f"{label_text} (1-{max_value})",
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
            # Convert inputs to integers
            focus = int(self.focus_round_entry.get())
            recharge = int(self.recharge_entry.get())
            big_recharge = int(self.extended_recharge_entry.get())
            cycles = int(self.cycles_entry.get())

            # Validate ranges
            if not (1 <= focus <= self.MAX_FOCUS_MINUTES):
                raise ValueError(f"Focus duration must be between 1 and {self.MAX_FOCUS_MINUTES} minutes")
            if not (1 <= recharge <= self.MAX_RECHARGE_MINUTES):
                raise ValueError(f"Recharge duration must be between 1 and {self.MAX_RECHARGE_MINUTES} minutes")
            if not (1 <= big_recharge <= self.MAX_BIG_RECHARGE_MINUTES):
                raise ValueError(f"Extended recharge duration must be between 1 and {self.MAX_BIG_RECHARGE_MINUTES} minutes")
            if not (1 <= cycles <= self.MAX_CYCLES):
                raise ValueError(f"Number of cycles must be between 1 and {self.MAX_CYCLES}")

            # Convert to seconds for the timer
            self.timer_controller.save_settings(
                focus * 60,
                recharge * 60,
                big_recharge * 60,
                cycles
            )
            self.destroy()
        except ValueError as e:
            # Show specific error message
            if str(e).startswith("invalid literal"):
                error_text = "Please enter valid numbers"
            else:
                error_text = str(e)

            self.error_label.configure(text=error_text)
            self.error_label.pack(pady=(0, 10))  # Simply pack it when needed