# src/tomatix/ui/main_ui.py
import customtkinter as ctk
import tkinter as tk
from tomatix.ui.statistics_view import StatisticsView
from tomatix.core.timer_controller import TimerController

class MainUI:
    """
    The primary UI for controlling the Tomatix timer. It integrates:
    - TimerController for logic and persistence
    - StatisticsView for displaying usage stats
    - A full-screen alert system to grab attention when cycles end
    """
    def __init__(self, root):
        self.root = root
        self.timer_controller = TimerController()
        self.timer_controller.on_mode_complete = self.handle_timer_completion

        self._setup_menu()
        self.statistics_view = StatisticsView(root, self.timer_controller)

        # Timer display widgets
        self.timer_label = ctk.CTkLabel(root, text="25:00", font=("Helvetica", 48))
        self.timer_label.pack(pady=20)

        self.mode_label = ctk.CTkLabel(root, text="Focus Round", font=("Helvetica", 20))
        self.mode_label.pack(pady=10)

        self._setup_controls()

        self.update_ui()

        # Bind Enter key to start/pause toggling
        self.root.bind("<Return>", self.toggle_timer)
        self.root.bind("<space>", self.toggle_timer)

    def _setup_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Configure Timer", command=self.open_settings_window)
        menu_bar.add_cascade(label="Settings", menu=settings_menu)

    def _setup_controls(self):
        """
        Initializes the buttons but does not display them immediately.
        Button visibility will be managed dynamically based on the timer state.
        """
        # Focus round count label
        self.current_focus_rounds_label = ctk.CTkLabel(self.root, text="0/4", font=("Helvetica", 24), anchor="center")
        self.current_focus_rounds_label.pack(pady=(10, 20))  # Place above the buttons

        # Buttons
        self.start_button = ctk.CTkButton(self.root, text="Start", command=self.start_timer)
        self.pause_button = ctk.CTkButton(self.root, text="Pause", command=self.pause_timer)
        self.reset_button = ctk.CTkButton(self.root, text="Reset", command=self.reset_timer)
        self.resume_button = ctk.CTkButton(self.root, text="Resume", command=self.start_timer)
        self.done_button = ctk.CTkButton(self.root, text="Done", command=self.done_action)

        # Display only relevant buttons initially
        self.update_buttons()

    def update_buttons(self):
        """
        Dynamically updates the button layout based on the current timer state.
        """
        state = self.timer_controller.get_state()
        running = state["running"]
        remaining_time = state["remaining_time"]
        full_time = self.timer_controller.timer.focus_round_duration

        # Hide all buttons initially
        self.start_button.pack_forget()
        self.pause_button.pack_forget()
        self.reset_button.pack_forget()
        self.resume_button.pack_forget()
        self.done_button.pack_forget()

        # Show buttons based on the state
        if not running and remaining_time == full_time:
            self.start_button.pack(side="top", pady=10)  # Center the START button
        elif running:
            self.pause_button.pack(side="left", padx=20, pady=10)
            self.reset_button.pack(side="left", padx=20, pady=10)
        elif not running and remaining_time < full_time:
            self.resume_button.pack(side="left", padx=20, pady=10)
            self.done_button.pack(side="left", padx=20, pady=10)

    def toggle_timer(self, event=None):
        if self.timer_controller.get_state()["running"]:
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):
        self.timer_controller.start()
        self.update_buttons()

    def pause_timer(self):
        self.timer_controller.pause()
        self.update_buttons()

    def reset_timer(self):
        self.timer_controller.reset()
        self.update_ui()
        self.update_buttons()

    def done_action(self):
        self.timer_controller.mark_done()
        self.update_buttons()

    def update_ui(self):
        state = self.timer_controller.update()
        mins, secs = divmod(state["remaining_time"], 60)
        self.timer_label.configure(text=f"{mins:02}:{secs:02}")
        self.mode_label.configure(text=state["mode"])

        # Update focus round count (e.g., 0/4)
        self.current_focus_rounds_label.configure(text=f"{state['current_focus_rounds']}/{self.timer_controller.timer.cycles}")

        self.root.after(200, self.update_ui)

    def handle_timer_completion(self, ended_mode):
        """
        React to a completed mode (Focus Round or Recharge).
        'ended_mode' indicates which mode just finished.
        """
        self.statistics_view.update_statistics()

        if ended_mode == "Focus Round":
            self.show_fullscreen_alert("Focus Round complete! Time for a recharge!")
        elif ended_mode == "Recharge":
            self.show_fullscreen_alert("Recharge over! Back to work!")
        elif ended_mode == "Extended Recharge":
            self.show_fullscreen_alert("Extended Recharge over! Let's get productive!")

    def show_fullscreen_alert(self, message):
        """
        Pops up a full-screen overlay with a message.
        The user can press Close, Escape, or Enter to dismiss it.
        """
        alert = ctk.CTkToplevel(self.root)
        alert.title("Alert")
        alert.attributes("-fullscreen", True)
        alert.configure(bg="black")

        message_label = ctk.CTkLabel(alert, text=message, font=("Helvetica", 48), text_color="white")
        message_label.pack(expand=True)

        close_button = ctk.CTkButton(alert, text="Close", command=alert.destroy, font=("Helvetica", 24))
        close_button.pack(pady=20)

        alert.bind("<Escape>", lambda e: alert.destroy())
        alert.bind("<Return>", lambda e: alert.destroy())
        alert.bind("<space>", lambda e: alert.destroy())

    def open_settings_window(self):
        """
        Opens a simple modal window to change Focus Round, recharge,
        and extended recharge durations in minutes.
        """
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
        """
        Validate user input and save new durations to the controller.
        If invalid integers are provided, show an error label instead.
        """
        try:
            focus_round_duration = int(focus_round) * 60
            recharge_duration = int(recharge) * 60
            big_recharge_duration = int(big_recharge) * 60

            self.timer_controller.save_settings(focus_round_duration, recharge_duration, big_recharge_duration)
            window.destroy()
        except ValueError:
            error_label = ctk.CTkLabel(window, text="Invalid input! Please enter integers.")
            error_label.pack(pady=5)
