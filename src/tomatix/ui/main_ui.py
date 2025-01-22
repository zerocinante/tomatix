# src/tomatix/ui/main_ui.py
import customtkinter as ctk
import tkinter as tk
from datetime import datetime

from tomatix.ui.statistics_view import StatisticsView
from tomatix.ui.focus_view import FocusView
from tomatix.ui.support_view import SupportView
from tomatix.ui.settings_window import SettingsWindow
from tomatix.ui.alert_window import AlertWindow
from tomatix.core.timer_controller import TimerController

class MainUI:
    """
    The primary UI coordinator for the Tomatix timer.
    Manages different views and handles high-level UI events.
    """
    def __init__(self, root, debug=False):
        self.debug = debug
        self.root = root
        self._debug_log("__init__ called")

        # Core components
        self.timer_controller = TimerController(debug=self.debug)

        # Hook up event handlers
        self.timer_controller.on_mode_complete = self.handle_timer_completion
        self.timer_controller.on_state_change = self.handle_state_change

        # View management
        self.current_view = "Focus"
        self.views = {}
        self._setup_views()
        self._setup_menu()

        # Initialize the UI update loop
        self.update_ui()

        # Switch to the Focus view on startup
        self.switch_view("Focus")

    def _debug_log(self, message):
        if self.debug:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            print(f"[DEBUG {self.__class__.__name__}] {now} - {message}")

    def _setup_views(self):
        """Initialize all view components."""
        self._debug_log("_setup_views called")

        # Create frames for each view
        self.views = {
            "Focus": FocusView(
                self.root,
                self.timer_controller,
                on_toggle=self.toggle_timer,
                on_mark_done=self.mark_done,
                debug=self.debug
            ),
            "Stats": StatisticsView(
                self.root,
                self.timer_controller,
                debug=self.debug
            ),
            "Support": SupportView(
                self.root,
                on_back=lambda: self.switch_view("Focus"),
                debug=self.debug
            )
        }

    def _setup_menu(self):
        """Creates the menu for switching views + Settings."""
        self._debug_log("_setup_menu called")

        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Toggle command flips between Focus and Stats
        self.menu_bar.add_command(label="Stats", command=self.toggle_view)
        self.toggle_cmd_index = self.menu_bar.index("end")

        # Settings and Donate commands
        self.menu_bar.add_command(label="⚙", command=self.open_settings_window)
        self.menu_bar.add_command(label="♨", command=lambda: self.switch_view("Support"))

    def toggle_view(self):
        """Toggle between Focus and Stats views."""
        self._debug_log("toggle_view called")

        if self.current_view == "Focus":
            self.switch_view("Stats")
            self.menu_bar.entryconfig(self.toggle_cmd_index, label="Tomatix")
        else:
            self.switch_view("Focus")
            self.menu_bar.entryconfig(self.toggle_cmd_index, label="Stats")

    def switch_view(self, view_name):
        """Hide all frames, then show the requested one."""
        self._debug_log(f"switch_view called with view_name={view_name}")

        # Hide any frame that might be on-screen
        for frame in self.views.values():
            frame.pack_forget()

        # Show the requested frame
        self.views[view_name].pack(fill="both", expand=True)
        self.current_view = view_name

        # Update view-specific bindings
        self._update_keybindings(view_name)

        # Refresh stats if showing stats view
        if view_name == "Stats":
            self.views["Stats"].update_statistics()

    def _update_keybindings(self, view_name):
        """Update keyboard shortcuts based on current view."""
        # Unbind all shortcuts first
        for key in ["<Return>", "<space>", "<Escape>"]:
            self.root.unbind(key)

        # Bind shortcuts for Focus view
        if view_name == "Focus":
            self.root.bind("<Return>", self.toggle_timer)
            self.root.bind("<space>", self.toggle_timer)

    def toggle_timer(self, event=None):
        """Start or pause the timer."""
        self._debug_log("toggle_timer called")
        state = self.timer_controller.get_state()
        if state["running"]:
            self.timer_controller.pause()
        else:
            self.timer_controller.start()

    def mark_done(self):
        """Mark the current cycle as complete."""
        self._debug_log("mark_done called")
        self.timer_controller.mark_done()

    def handle_timer_completion(self, ended_mode):
        """Handle completion of a timer cycle."""
        self._debug_log(f"handle_timer_completion called with ended_mode={ended_mode}")

        # Update statistics
        self.views["Stats"].update_statistics()

        # Show completion alert
        message = self._get_completion_message(ended_mode)
        AlertWindow(self.root, message, self.switch_view, debug=self.debug)

    def _get_completion_message(self, ended_mode):
        """Get the appropriate message for the completion alert."""
        messages = {
            "Focus Round": "Focus Round complete! Time for a recharge!",
            "Recharge": "Recharge over! Back to work!",
            "Extended Recharge": "Extended Recharge over! Let's get productive!"
        }
        return messages.get(ended_mode, "Timer complete!")

    def handle_state_change(self, state):
        """Handle timer state changes."""
        self._debug_log(f"handle_state_change called with state={state}")
        # TODO: we removed update_buttons from here, should we add it back?
        if self.current_view == "Focus": # TODO: Should we do this for all views?
            self.views["Focus"].handle_state_change(state)

    def update_ui(self):
        """Periodically updates the UI with the current timer state."""
        if self.current_view == "Focus":
            self.views["Focus"].update_ui()
        self.root.after(200, self.update_ui)

    def open_settings_window(self):
        """Opens the settings window for timer configuration."""
        self._debug_log("open_settings_window called")
        SettingsWindow(self.root, self.timer_controller, debug=self.debug)
