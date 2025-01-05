# src/tomatix/ui/statistics_view.py
import customtkinter as ctk

class StatisticsView:
    """
    A separate widget for displaying Focus Round statistics.
    We pass in the timer_controller so it can access Persistence data.
    """
    def __init__(self, root, timer):
        self.timer = timer

        # Display label for quick daily stats
        self.stats_label = ctk.CTkLabel(root, text="Last 7 Days:", font=("Helvetica", 16), anchor="w")
        self.stats_label.pack(pady=(0, 20), padx=20, anchor="w")

        self.update_statistics()

    def update_statistics(self):
        """
        Fetch data from the persistence layer and display it in a text format.
        """
        stats = self.timer.persistence_manager.get_statistics()
        daily_stats = "\n".join(
            f"{day}: {count} Focus Rounds ({minutes} minutes)"
            for day, count, minutes in stats[:7]
        )
        self.stats_label.configure(text=f"Last 7 Days:\n{daily_stats}")
