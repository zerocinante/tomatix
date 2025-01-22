import customtkinter as ctk
from datetime import datetime

class FocusView(ctk.CTkFrame):
    """Main timer view showing the countdown and controls."""

    def __init__(self, parent, timer_controller, on_toggle=None, on_mark_done=None, debug=False):
        super().__init__(parent)
        self.debug = debug
        self.timer_controller = timer_controller
        self.on_toggle = on_toggle
        self.on_mark_done = on_mark_done
        self._debug_log("__init__ called")

        self._setup_ui()

    def _debug_log(self, message):
        if self.debug:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            print(f"[DEBUG {self.__class__.__name__}] {now} - {message}")

    def _setup_ui(self):
        """Create and arrange the UI elements."""
        # Mode label (Focus Round, Recharge, etc.)
        self.mode_label = ctk.CTkLabel(
            self,
            text="Focus Round",
            font=("Helvetica", 24)
        )
        self.mode_label.pack(pady=(20, 0))

        # Timer display
        self.time_label = ctk.CTkLabel(
            self,
            text="25:00",
            font=("Helvetica", 48)
        )
        self.time_label.pack(pady=(20, 0))

        # Current focus rounds label
        self.rounds_label = ctk.CTkLabel(
            self,
            text="0/4",
            font=("Helvetica", 24)
        )
        self.rounds_label.pack(pady=(10, 20))

        # Button frame for layout
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.pack(pady=(0, 20))

        # Create all possible buttons (initially hidden)
        self.start_button = ctk.CTkButton(
            self.button_frame,
            text="Start",
            command=self._handle_toggle,
            width=200
        )

        self.pause_button = ctk.CTkButton(
            self.button_frame,
            text="Pause",
            command=self._handle_toggle,
            width=200
        )

        self.resume_button = ctk.CTkButton(
            self.button_frame,
            text="Resume",
            command=self._handle_toggle,
            width=200
        )

        self.reset_button = ctk.CTkButton(
            self.button_frame,
            text="Reset",
            command=self._handle_reset,
            width=200
        )

        self.done_button = ctk.CTkButton(
            self.button_frame,
            text="Done",
            command=self._handle_mark_done,
            width=200
        )

        # Show initial button state
        self._update_buttons({"running": False, "remaining_time": self.timer_controller.get_full_time()})

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
            button.pack_forget()

        running = state["running"]
        remaining_time = state["remaining_time"]
        full_time = self.timer_controller.get_full_time()
        timer_started = remaining_time < full_time

        if not running:
            if not timer_started:
                # Timer hasn't started yet - show Start
                self.start_button.pack(pady=(0, 10))
            else:
                # Timer is paused - show Resume and Done
                self.resume_button.pack(pady=(0, 10))
                self.done_button.pack()
        else:
            # Timer is running - show Pause and Reset
            self.pause_button.pack(pady=(0, 10))
            self.reset_button.pack()

    def handle_state_change(self, state):
        """Update UI elements based on timer state."""
        self._debug_log(f"handle_state_change called with {state}")

        # Update mode label
        self.mode_label.configure(text=state["mode"])

        # Update rounds display
        if state["mode"] == "Focus Round":
            rounds_text = f"{state['current_focus_rounds']}/4"
            self.rounds_label.configure(text=rounds_text)

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