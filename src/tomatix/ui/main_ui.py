# src/tomatix/ui/main_ui.py
import customtkinter as ctk
import tkinter as tk
from datetime import datetime

from tomatix.ui.statistics_view import StatisticsView
from tomatix.core.timer_controller import TimerController

class MainUI:
    """
    The primary UI for controlling the Tomatix timer.
    Integrates:
    - TimerController for logic and persistence
    - StatisticsView for displaying usage stats
    - A full-screen alert system to grab attention when cycles end
    """

    def __init__(self, root, debug=False):
        self.debug = debug
        self.root = root
        self._debug_log("__init__ called")

        # Timer controller
        self.timer_controller = TimerController(debug=self.debug)
        # Hook up event handlers
        self.timer_controller.on_mode_complete = self.handle_timer_completion
        self.timer_controller.on_state_change = self.handle_state_change

        # Keep track of the current view
        self.current_view = "Focus"

        # Create frames (Focus and Stats)
        self.focus_frame = None
        self.stats_frame = None
        self.views = {}  # Will hold references to frames by name

        self._setup_frames()
        self._setup_menu()

        # Initialize the UI update loop
        self.update_ui()

        # Show the Focus view on startup
        self.show_focus_view()

    def _debug_log(self, message):
        if self.debug:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            print(f"[DEBUG {self.__class__.__name__}] {now} - {message}")

    def _setup_menu(self):
        """Creates the menu for switching views + Settings."""
        self._debug_log("_setup_menu called")

        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Toggle command flips between Focus and Stats
        self.menu_bar.add_command(label="Stats", command=self.toggle_view)
        self.toggle_cmd_index = self.menu_bar.index("end")

        # Add the settings command
        self.menu_bar.add_command(label="⚙", command=self.open_settings_window)

    def _setup_frames(self):
        """Create the two main frames: Focus and Stats."""
        self._debug_log("_setup_frames called")
        # -- Focus Frame --
        self.focus_frame = ctk.CTkFrame(self.root)
        self._setup_focus_view_widgets()

        # -- Stats Frame --
        self.stats_frame = ctk.CTkFrame(self.root)
        self._setup_stats_view_widgets()

        # Put them in a dictionary for easy switching
        self.views = {
            "Focus": self.focus_frame,
            "Stats": self.stats_frame
        }

    def toggle_view(self):
        """
        Toggle between Focus and Stats views, and rename the menu item accordingly.
        """
        self._debug_log("toggle_view called")

        if self.current_view == "Focus":
            self.show_stats_view()
            self.menu_bar.entryconfig(self.toggle_cmd_index, label="Tomatix")
            self.current_view = "Stats"
        else:
            self.show_focus_view()
            self.menu_bar.entryconfig(self.toggle_cmd_index, label="Stats")
            self.current_view = "Focus"

    def switch_view(self, view_name):
        """Hide all frames, then show the requested one."""
        self._debug_log(f"switch_view called with view_name={view_name}")

        # Hide any frame that might be on-screen
        for frame in self.views.values():
            frame.pack_forget()

        # Show the requested frame
        self.views[view_name].pack(fill="both", expand=True)
        self.current_view = view_name

        # Rebind or unbind certain keys based on the view
        if view_name == "Focus":
            self.root.bind("<Return>", self.toggle_timer)
            self.root.bind("<space>", self.toggle_timer)
            self.root.unbind("<Escape>")
        else:
            self.root.unbind("<Return>")
            self.root.unbind("<space>")
            self.root.unbind("<Escape>")

    def _setup_focus_view_widgets(self):
        """Layout the timer display and controls inside the focus_frame."""
        self._debug_log("_setup_focus_view_widgets called")

        # Timer label
        self.timer_label = ctk.CTkLabel(
            self.focus_frame, text="25:00", font=("Helvetica", 48), width=200, anchor="center"
        )
        self.timer_label.pack(pady=20)

        # Mode label
        self.mode_label = ctk.CTkLabel(self.focus_frame, text="Focus Round", font=("Helvetica", 20))
        self.mode_label.pack(pady=10)

        # Current focus rounds label
        self.current_focus_rounds_label = ctk.CTkLabel(
            self.focus_frame, text="0/4", font=("Helvetica", 24), anchor="center"
        )
        self.current_focus_rounds_label.pack(pady=(10, 20))

        # Buttons frame
        self.button_frame = ctk.CTkFrame(self.focus_frame)
        self.button_frame.pack(pady=(0, 20))

        # Actual Buttons
        self.start_button = ctk.CTkButton(self.button_frame, text="Start", command=self.start_timer, width=100)
        self.pause_button = ctk.CTkButton(self.button_frame, text="Pause", command=self.pause_timer, width=100)
        self.reset_button = ctk.CTkButton(self.button_frame, text="Reset", command=self.reset_timer, width=100)
        self.resume_button = ctk.CTkButton(self.button_frame, text="Resume", command=self.start_timer, width=100)
        self.done_button = ctk.CTkButton(self.button_frame, text="Done", command=self.done_action, width=100)

        self.update_buttons()

    def _setup_stats_view_widgets(self):
        """Layout the statistics view inside the stats_frame."""
        self._debug_log("_setup_stats_view_widgets called")
        self.statistics_view = StatisticsView(self.stats_frame, self.timer_controller, debug=self.debug)

    def show_focus_view(self):
        """Show the focus (timer) frame and hide the stats frame."""
        self._debug_log("Showing Focus View.")
        self.switch_view("Focus")

    def show_stats_view(self):
        """Show the stats frame and hide the focus (timer) frame."""
        self._debug_log("Showing Stats View.")
        self.switch_view("Stats")
        self.statistics_view.update_statistics()

    def update_buttons(self):
        """Update button visibility based on the current timer state."""
        self._debug_log("update_buttons called")
        state = self.timer_controller.get_state()
        running = state["running"]
        remaining_time = state["remaining_time"]
        full_time = self.timer_controller.get_full_time()

        # Hide all buttons first
        for widget in self.button_frame.winfo_children():
            widget.pack_forget()

        # Show relevant buttons
        if not running and remaining_time == full_time:
            self.start_button.pack(side="top", padx=10)
        elif running:
            self.pause_button.pack(side="left", padx=10)
            self.reset_button.pack(side="left", padx=10)
        elif not running and remaining_time < full_time:
            self.resume_button.pack(side="left", padx=10)
            self.done_button.pack(side="left", padx=10)

    def toggle_timer(self, event=None):
        """Toggles between Start and Pause states."""
        self._debug_log("toggle_timer called")
        if self.timer_controller.get_state()["running"]:
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):
        self._debug_log("start_timer called")
        self.timer_controller.start()

    def pause_timer(self):
        self._debug_log("pause_timer called")
        self.timer_controller.pause()

    def reset_timer(self):
        self._debug_log("reset_timer called")
        self.timer_controller.reset()

    def done_action(self):
        self._debug_log("done_action called")
        self.timer_controller.mark_done()

    def handle_state_change(self, state):
        self._debug_log(f"handle_state_change called with state={state}")
        self.update_buttons()

    def update_ui(self):
        """Periodically updates the UI with the current timer state."""
        state = self.timer_controller.update()
        mins, secs = map(int, divmod(state["remaining_time"], 60))
        self.timer_label.configure(text=f"{mins:02}:{secs:02}")
        self.mode_label.configure(text=state["mode"])
        self.current_focus_rounds_label.configure(
            text=f"{state['current_focus_rounds']}/{self.timer_controller.timer.cycles}"
        )

        self.root.after(200, self.update_ui)

    def handle_timer_completion(self, ended_mode):
        """Handles completion of a timer cycle."""
        self._debug_log(f"handle_timer_completion called with ended_mode={ended_mode}")
        self.statistics_view.update_statistics()

        if ended_mode == "Focus Round":
            self.show_fullscreen_alert("Focus Round complete! Time for a recharge!")
        elif ended_mode == "Recharge":
            self.show_fullscreen_alert("Recharge over! Back to work!")
        elif ended_mode == "Extended Recharge":
            self.show_fullscreen_alert("Extended Recharge over! Let's get productive!")

    def show_fullscreen_alert(self, message):
        """Displays a full-screen alert for timer completion."""
        self._debug_log("show_fullscreen_alert called")

        # Make clear and make fullscreen the main window
        self.root.attributes("-fullscreen", True)
        # Hide all main frames
        for frame in self.views.values():
            frame.pack_forget()

        # Create the alert message label
        self.alert_message_label = ctk.CTkLabel(
            self.root,
            text=message,
            font=("Helvetica", 48),
            text_color="white",
            anchor="center"
        )
        self.alert_message_label.pack(expand=True)

        # Create the close button
        self.alert_close_button = ctk.CTkButton(
            self.root,
            text="Close",
            command=self.dismiss_fullscreen_alert,
            font=("Helvetica", 24)
        )
        self.alert_close_button.pack(pady=20)

        self.root.bind("<Escape>", self.dismiss_fullscreen_alert)
        self.root.bind("<Return>", self.dismiss_fullscreen_alert)
        self.root.bind("<space>", self.dismiss_fullscreen_alert)

    def dismiss_fullscreen_alert(self, event=None):
        """Dismiss the fullscreen alert and restore the timer view."""
        self._debug_log("dismiss_fullscreen_alert called")

        # Destroy the alert message and button
        if hasattr(self, 'alert_message_label'):
            self.alert_message_label.destroy()
        if hasattr(self, 'alert_close_button'):
            self.alert_close_button.destroy()

        # Exit fullscreen mode
        self.root.attributes("-fullscreen", False)

        # Restore the timer view
        if self.current_view == "Focus":
            self.show_focus_view()
        else:
            self.show_stats_view()

    def open_settings_window(self):
        """Opens the settings window for timer configuration."""
        self._debug_log("open_settings_window called")
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("Configure Timer")

        focus_round_label = ctk.CTkLabel(settings_window, text="Focus Round Duration (min):")
        focus_round_label.pack(pady=5)
        focus_round_entry = ctk.CTkEntry(settings_window)
        focus_round_entry.insert(0, str(self.timer_controller.timer.focus_round_duration // 60))
        focus_round_entry.pack(pady=5)

        recharge_label = ctk.CTkLabel(settings_window, text="Recharge Duration (min):")
        recharge_label.pack(pady=5)
        recharge_entry = ctk.CTkEntry(settings_window)
        recharge_entry.insert(0, str(self.timer_controller.timer.recharge // 60))
        recharge_entry.pack(pady=5)

        big_recharge_label = ctk.CTkLabel(settings_window, text="Extended Recharge Duration (min):")
        big_recharge_label.pack(pady=5)
        big_recharge_entry = ctk.CTkEntry(settings_window)
        big_recharge_entry.insert(0, str(self.timer_controller.timer.big_recharge // 60))
        big_recharge_entry.pack(pady=5)

        save_button = ctk.CTkButton(
            settings_window,
            text="Save",
            command=lambda: self.save_settings(
                focus_round_entry.get(),
                recharge_entry.get(),
                big_recharge_entry.get(),
                settings_window
            )
        )
        save_button.pack(pady=20)

    def save_settings(self, focus_round, recharge, big_recharge, window):
        """Save updated timer settings."""
        self._debug_log("save_settings called")
        try:
            focus_round_duration = int(focus_round) * 60
            recharge_duration = int(recharge) * 60
            big_recharge_duration = int(big_recharge) * 60

            self.timer_controller.save_settings(focus_round_duration, recharge_duration, big_recharge_duration)
            window.destroy()
        except ValueError:
            error_label = ctk.CTkLabel(window, text="Invalid input! Please enter integers.")
            error_label.pack(pady=5)
