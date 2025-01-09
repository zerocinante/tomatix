# src/tomatix/ui/statistics_view.py
import customtkinter as ctk
from datetime import datetime

class StatisticsView:
    """
    A separate widget for displaying Focus Round statistics.
    We pass in the timer_controller so it can access Persistence data.
    """
    def __init__(self, root, timer_controller, debug=False):
        self.debug = debug
        self._debug_log("__init__ called")
        self.timer_controller = timer_controller

        # Display label for today's stats
        self.stats_label = ctk.CTkLabel(root, text="Today: 0 Focus Rounds, 0 minutes", font=("Helvetica", 16), anchor="w")
        self.stats_label.pack(pady=(0, 20), padx=20, anchor="w")

        self.update_statistics()

    def _debug_log(self, message):
        if self.debug:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Timestamp with milliseconds
            print(f"[DEBUG {self.__class__.__name__}] {now} - {message}")

    def update_statistics(self):
        """
        Fetch today's stats and display them.
        """
        self._debug_log("update_statistics called")
        total_focus_rounds, total_minutes = self.timer_controller.persistence_manager.get_today_stats()

        # Update the stats label with today's data
        stats_text = f"Today: {total_focus_rounds} Focus Rounds, {total_minutes} minutes"
        self.stats_label.configure(text=stats_text)
