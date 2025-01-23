# src/tomatix/ui/statistics_view.py
import customtkinter as ctk
from tomatix.ui.views.base_view import BaseView

class StatisticsView(BaseView):
    """A minimalist view for displaying Focus Round statistics."""

    def __init__(self, root, timer_controller, on_back=None, colors=None, debug=False):
        super().__init__(root, on_back, debug)
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
        self._setup_ui()

    def _setup_ui(self):
        """Create and arrange the UI elements."""
        # Center content frame
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(padx=10, pady=10, expand=True)

        # Stats title
        self.title_label = ctk.CTkLabel(
            content,
            text="Today's Progress",
            font=("SF Pro Display", 24),
            text_color="#FFFFFF"
        )
        self.title_label.pack(pady=(0, 20))

        # Stats frame
        stats_frame = ctk.CTkFrame(content, fg_color="transparent")
        stats_frame.pack(pady=(0, 30))

        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="0 Focus Rounds\n0 Minutes",
            font=("SF Pro Display", 36),
            text_color="#FF7F50"
        )
        self.stats_label.pack()

        # Back button
        ctk.CTkButton(
            self,
            text="Back to Focus",
            command=self.on_back,
            width=200,
            height=32,
            corner_radius=16,
            font=("SF Pro Display", 14),
            fg_color="transparent",
            hover_color=self.colors["accent"],
            text_color=self.colors["text"]
        ).pack(pady=(0, 20))

    def update_statistics(self):
        """Update the statistics display."""
        total_focus_rounds, total_minutes = self.timer_controller.persistence_manager.get_today_stats()
        stats_text = f"{total_focus_rounds} Focus Rounds\n{total_minutes} Minutes"
        self.stats_label.configure(text=stats_text)

    def pack(self, *args, **kwargs):
        super().pack(*args, **kwargs)
        self.update_statistics()
