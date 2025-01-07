# src/tomatix/core/timer_controller.py
import time
from tomatix.core.timer import Timer
from tomatix.core.persistence import PersistenceManager

class TimerController:
    """
    Orchestrates the Timer (pure logic) and Persistence (database).
    The UI should call this controller rather than the raw Timer.
    """
    def __init__(
        self,
        persistence_manager=None,
        focus_round_duration=25*60,
        recharge=5*60,
        big_recharge=20*60,
        cycles=4,
    ):
        self.persistence_manager = persistence_manager or PersistenceManager()
        self.timer = Timer(
            focus_round_duration=focus_round_duration,
            recharge=recharge,
            big_recharge=big_recharge,
            cycles=cycles
        )

        # The UI can set a callback for when a mode finishes
        self.on_mode_complete = None

        self._load_or_init_settings()

    def _load_or_init_settings(self):
        """
        If settings exist in the database, load them into the Timer.
        Otherwise, we use the default durations passed in the constructor.
        """
        settings = self.persistence_manager.load_settings()
        if settings:
            self.timer.set_durations(*settings)

    def start(self):
        self.timer.start()

    def pause(self):
        self.timer.pause()

    def mark_done(self):
        self.timer.mark_done()
        self._handle_completion()

    def reset(self):
        self.timer.reset()

    def get_state(self):
        return self.timer.get_state()

    def save_settings(self, focus_round, recharge, big_recharge):
        """
        Persist user-updated durations in the DB so we can restore
        them next time the app launches.
        """
        self.timer.set_durations(focus_round, recharge, big_recharge)
        self.persistence_manager.save_settings(focus_round, recharge, big_recharge)

    def update(self):
        """
        Called periodically by the UI to update the Timer state.
        If the timer hits 0, we handle the completion logic here.
        """
        previous_mode = self.timer.current_mode
        state = self.get_state()

        # If the Timer just finished
        if state["remaining_time"] == 0:
            self._handle_completion(previous_mode)

        return state

    def _handle_completion(self, previous_mode=None):
        """
        Called when a cycle ends (either Focus Round or Recharge).
        1. Log partial or full Focus Round time if we just ended a Focus Round.
        2. Switch to the next mode.
        3. Notify the UI via on_mode_complete if provided.
        """

        previous_mode = previous_mode or self.timer.current_mode

        elapsed_minutes = self.timer.get_elapsed_minutes()
        if previous_mode == "Focus Round":
            self.persistence_manager.log_focus_round(elapsed_minutes)

        self.timer.next_mode()

        if self.on_mode_complete:
            self.on_mode_complete(previous_mode)

    def get_full_time(self):
        """
        Returns the full time for the current mode.
        """
        if self.timer.current_mode == "Focus Round":
            return self.timer.focus_round_duration
        elif self.timer.current_mode == "Recharge":
            return self.timer.recharge
        elif self.timer.current_mode == "Extended Recharge":
            return self.timer.big_recharge
        return 0  # Fallback
