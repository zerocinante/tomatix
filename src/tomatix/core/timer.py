# src/tomatix/core/timer.py
import time

class Timer:
    """
    A low-level class responsible for timing logic only.
    It does not handle UI or persistence.
    """
    def __init__(
        self,
        focus_round_duration=25*60,
        recharge=5*60,
        big_recharge=20*60,
        cycles=4
    ):
        self.focus_round_duration = focus_round_duration
        self.recharge = recharge
        self.big_recharge = big_recharge
        self.cycles = cycles

        self.current_mode = "Focus Round"
        self.running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.remaining_time = self.focus_round_duration

        self.current_focus_rounds = 0
        self.total_focus_rounds = 0

    def set_durations(self, focus_round, recharge, big_recharge):
        """
        Update durations mid-run if the user changes settings.
        We reset to avoid confusion between old durations and new ones.
        """
        self.focus_round_duration = focus_round
        self.recharge = recharge
        self.big_recharge = big_recharge
        self.reset()

    def start(self):
        if not self.running:
            self.running = True
            # Subtract any previously accumulated elapsed_time so we can resume
            self.start_time = time.time() - self.elapsed_time

    def pause(self):
        if self.running:
            self.running = False
            # Capture how long we ran
            self.elapsed_time = time.time() - self.start_time

    def mark_done(self):
        """
        Force-end the current cycle early by setting remaining_time to 0.
        We also finalize elapsed_time if we were running.
        """
        if self.running:
            self.elapsed_time = time.time() - self.start_time

        self.running = False
        self.remaining_time = 0

    def reset(self):
        """
        Reset the timer to a fresh state for the current mode, discarding
        any partial progress.
        """
        self.running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.remaining_time = self._get_duration()

    def get_state(self):
        """
        Returns a dict describing the current timer status.
        This is meant for the UI/controller to poll frequently.
        """
        if self.running:
            # Continuously update the countdown
            self.elapsed_time = time.time() - self.start_time
            self.remaining_time = max(0, self._get_duration() - int(self.elapsed_time))

        return {
            "mode": self.current_mode,
            "remaining_time": self.remaining_time,
            "current_focus_rounds": self.current_focus_rounds,
            "total_focus_rounds": self.total_focus_rounds,
            "running": self.running,
        }

    def get_elapsed_minutes(self):
        """
        Returns how many whole minutes have been used in this cycle.
        Useful for partial logging (i.e., mark_done) or final logging at cycle end.
        """
        if self.running:
            self.elapsed_time = time.time() - self.start_time
        return int(self.elapsed_time // 60)

    def next_mode(self):
        """
        Move to the next mode in the cycle. If we just finished a Focus Round,
        we either go to Recharge or Extended Recharge. If we finished a recharge,
        we return to Focus Round. The cycle resets when we've completed 'cycles' focus_rounds.
        """
        if self.current_mode == "Focus Round":
            self.total_focus_rounds += 1
            self.current_focus_rounds += 1
            # After 'cycles' focus_rounds, move to an extended recharge
            if self.current_focus_rounds >= self.cycles:
                self.current_mode = "Extended Recharge"
                self.current_focus_rounds = 0
            else:
                self.current_mode = "Recharge"
        else:
            # Any recharge leads back to a Focus Round
            self.current_mode = "Focus Round"

        # Reset everything for the new mode
        self.reset()

    def _get_duration(self):
        # Return how many seconds this cycle should run based on current_mode
        if self.current_mode == "Focus Round":
            return self.focus_round_duration
        elif self.current_mode == "Recharge":
            return self.recharge
        elif self.current_mode == "Extended Recharge":
            return self.big_recharge
