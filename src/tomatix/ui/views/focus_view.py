import customtkinter as ctk
from datetime import datetime
from tomatix.ui.views.base_view import BaseView

class FocusView(BaseView):
    """Main timer view showing the countdown and controls."""

    def __init__(self, parent, timer_controller, on_toggle=None, on_mark_done=None, colors=None, debug=False):
        super().__init__(parent, debug=debug, on_back=None)
        self.timer_controller = timer_controller
        self.on_toggle = on_toggle
        self.on_mark_done = on_mark_done
        self.colors = colors or {  # Fallback colors if none provided
            "primary": "#3B8ED0",
            "secondary": "#666666",
            "background": "#2B2B2B",
            "text": "#FFFFFF",
            "success": "#4CAF50",
            "warning": "#FFC107"
        }
        self._debug_log("__init__ called")

        self._setup_ui()
        # Explicitly update buttons with initial state
        initial_state = {
            "running": False,
            "remaining_time": self.timer_controller.get_full_time(),
            "mode": "Focus Round",
            "current_focus_rounds": 1
        }
        self._update_buttons(initial_state)

    def _debug_log(self, message):
        if self.debug:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            print(f"[DEBUG {self.__class__.__name__}] {now} - {message}")

    def _setup_ui(self):
        """Create and arrange the UI elements."""
        # Use pack instead of grid for more flexible sizing
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(padx=10, pady=10, expand=True)

        # Compact timer display
        self.time_label = ctk.CTkLabel(
            content,
            text="25:00",
            font=("SF Pro Display", 36),
            text_color=self.colors["text"]
        )
        self.time_label.pack(pady=(0, 10))

        # Info frame (mode and rounds)
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(pady=(0, 10))

        # Mode label (top line)
        self.mode_label = ctk.CTkLabel(
            info_frame,
            text="FOCUS",
            font=("SF Pro Display", 12),
            text_color=self.colors["secondary"]
        )
        self.mode_label.pack()

        # Progress label (bottom line)
        self.progress_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=("SF Pro Display", 12),
            text_color=self.colors["secondary"]
        )
        self.progress_label.pack()

        # Fixed-size button container
        button_container = ctk.CTkFrame(content, fg_color="transparent", height=40)
        button_container.pack(pady=(0, 10), fill="x")
        button_container.pack_propagate(False)  # Prevent size changes

        # Button frame inside container
        self.button_frame = ctk.CTkFrame(button_container, fg_color="transparent")
        self.button_frame.pack(expand=True)

        # Create all possible buttons (initially hidden)
        button_configs = [
            ("start_button", "▶", self._handle_toggle),
            ("pause_button", "⏸", self._handle_toggle),
            ("resume_button", "▶", self._handle_toggle),
            ("reset_button", "⟳", self._handle_reset),
            ("done_button", "✓", self._handle_mark_done)
        ]

        for i, (attr_name, symbol, command) in enumerate(button_configs):
            button = ctk.CTkButton(
                self.button_frame,
                text=symbol,
                command=command,
                width=30,
                height=30,
                corner_radius=15
            )
            setattr(self, attr_name, button)

    def _handle_toggle(self):
        """Local handler for toggle button."""
        if self.on_toggle:
            self.on_toggle()

    def _handle_mark_done(self):
        """Local handler for mark done button."""
        if self.on_mark_done:
            self.on_mark_done()

    def _handle_reset(self):
        """Local handler for reset button."""
        self.timer_controller.reset()

    def _update_buttons(self, state):
        """Update button visibility based on timer state."""
        # Hide all buttons first
        for button in [self.start_button, self.pause_button, self.resume_button,
                      self.reset_button, self.done_button]:
            button.grid_forget()

        running = state.get("running", False)  # Default to False if not present
        remaining_time = state.get("remaining_time", self.timer_controller.get_full_time())
        full_time = self.timer_controller.get_full_time()
        timer_started = remaining_time < full_time

        if not running:
            if not timer_started:
                # Timer hasn't started yet - show Start
                self.start_button.grid(row=0, column=0, padx=5)
            else:
                # Timer is paused - show Resume and Done
                self.resume_button.grid(row=0, column=0, padx=5)
                self.done_button.grid(row=0, column=1, padx=5)
        else:
            # Timer is running - show Pause and Reset
            self.pause_button.grid(row=0, column=0, padx=5)
            self.reset_button.grid(row=0, column=1, padx=5)

    def handle_state_change(self, state):
        """Update UI elements based on timer state."""
        self._debug_log(f"handle_state_change called with {state}")

        total_cycles = self.timer_controller.timer.cycles

        # Update mode label with a more intuitive display
        if state["mode"] == "Focus Round":
            # Show current round number (add 1 since core counts from 0)
            current_round = state["current_focus_rounds"] + 1
            self.mode_label.configure(text=f"ROUND {current_round}")
            # Show progress on second line
            self.progress_label.configure(text=f"({current_round}/{total_cycles})")
        else:
            # During breaks, just show the mode name
            self.mode_label.configure(text=state["mode"].upper())
            self.progress_label.configure(text="")

        # Update buttons
        self._update_buttons(state)

    def update_ui(self):
        """Update the time display."""
        state = self.timer_controller.get_state()
        remaining = state["remaining_time"]

        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        time_text = f"{minutes:02d}:{seconds:02d}"

        self.time_label.configure(text=time_text)

    def bind_keys(self, root):
        """Bind view-specific keyboard shortcuts."""
        # Don't call super().bind_keys() since Focus view doesn't need Escape
        root.bind("<Return>", self.on_toggle)
        root.bind("<space>", self.on_toggle)

    def unbind_keys(self, root):
        """Unbind view-specific keyboard shortcuts."""
        root.unbind("<Return>")
        root.unbind("<space>")