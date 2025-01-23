# src/tomatix/ui/statistics_view.py
import customtkinter as ctk
from datetime import datetime
from tomatix.ui.views.base_view import BaseView

class StatisticsView(BaseView):
    """
    A separate widget for displaying Focus Round statistics.
    We pass in the timer_controller so it can access Persistence data.
    """
    def __init__(self, root, timer_controller, on_back=None, debug=False):
        super().__init__(root, on_back, debug)
        self.timer_controller = timer_controller

        # Subscribe to timer completion events
        self.timer_controller.add_mode_complete_callback(self._on_timer_complete)

        # Display label for today's stats
        self.stats_label = ctk.CTkLabel(
            self,
            text="Today: 0 Focus Rounds, 0 minutes",
            font=("Helvetica", 16),
            anchor="w"
        )
        self.stats_label.pack(pady=(0, 20), padx=20, anchor="w")

        # Add back button from base class
        self._add_back_button()

        self.update_statistics()

    def update_statistics(self):
        """
        Fetch today's stats and display them.
        """
        self._debug_log("update_statistics called")
        total_focus_rounds, total_minutes = self.timer_controller.persistence_manager.get_today_stats()

        # Update the stats label with today's data
        stats_text = f"Today: {total_focus_rounds} Focus Rounds, {total_minutes} minutes"
        self.stats_label.configure(text=stats_text)

    def _on_timer_complete(self, ended_mode):
        """Handle timer completion events."""
        self._debug_log(f"_on_timer_complete called with ended_mode={ended_mode}")
        self.update_statistics()

    def pack(self, *args, **kwargs):
        """Override pack to update statistics when view becomes visible."""
        super().pack(*args, **kwargs)
        self.update_statistics()
