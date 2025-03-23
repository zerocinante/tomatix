# src/tomatix/core/timer_controller.py
import time
from tomatix.core.timer import Timer
from tomatix.core.persistence import PersistenceManager
from datetime import datetime

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
        debug=False
    ):
        self.debug = debug
        self._debug_log("__init__ called")

        self.persistence_manager = persistence_manager or PersistenceManager(debug=self.debug)
        self.timer = Timer(
            focus_round_duration=focus_round_duration,
            recharge=recharge,
            big_recharge=big_recharge,
            cycles=cycles,
            debug=self.debug
        )

        # Replace single callbacks with lists of callbacks
        self.mode_complete_callbacks = []
        self.state_change_callbacks = []

        # Initialize last state for change detection
        self._last_comparable_state = {
            "running": False,
            "mode": self.timer.current_mode,
            "current_focus_rounds": 0,
        }

        self._load_or_init_settings()

    def _debug_log(self, message):
        if self.debug:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # Timestamp with milliseconds
            print(f"[DEBUG {self.__class__.__name__}] {now} - {message}")

    def _load_or_init_settings(self):
        """
        If settings exist in the database, load them into the Timer.
        Otherwise, we use the default durations passed in the constructor.
        """
        self._debug_log("_load_or_init_settings called")
        settings = self.persistence_manager.load_settings()
        if settings:
            self.timer.set_durations(*settings)

    def start(self):
        self._debug_log("start called")
        self.timer.start()
        self._check_and_notify_state_change()

    def pause(self):
        self._debug_log("pause called")
        self.timer.pause()
        self._check_and_notify_state_change()

    def mark_done(self):
        self._debug_log("mark_done called")
        self.timer.mark_done()
        self._handle_completion()

    def reset(self):
        self._debug_log("reset called")
        self.timer.reset()
        self._check_and_notify_state_change()

    def get_state(self):
        #self._debug_log("get_state called")
        return self.timer.get_state()

    def save_settings(self, focus_round, recharge, big_recharge, cycles):
        """
        Persist user-updated durations in the DB so we can restore
        them next time the app launches.
        """
        self._debug_log(f"save_settings called with {focus_round=}, {recharge=}, {big_recharge=}, {cycles=}")
        self.timer.set_durations(focus_round, recharge, big_recharge, cycles)
        self.persistence_manager.save_settings(focus_round, recharge, big_recharge, cycles)
        self._check_and_notify_state_change()

    def update(self):
        """
        Called periodically by the UI to update the Timer state.
        If the timer hits 0, we handle the completion logic here.
        """
        # self._debug_log("update called")  # too frequent
        previous_mode = self.timer.current_mode
        state = self.get_state()

        # If the Timer just finished
        if state["remaining_time"] == 0:
            self._handle_completion(previous_mode)

        return state

    def add_mode_complete_callback(self, callback):
        """Add a callback to be notified when a mode completes."""
        self._debug_log(f"add_mode_complete_callback called")
        if callback not in self.mode_complete_callbacks:
            self.mode_complete_callbacks.append(callback)

    def remove_mode_complete_callback(self, callback):
        """Remove a mode complete callback."""
        self._debug_log(f"remove_mode_complete_callback called")
        if callback in self.mode_complete_callbacks:
            self.mode_complete_callbacks.remove(callback)

    def add_state_change_callback(self, callback):
        """Add a callback to be notified when state changes."""
        self._debug_log(f"add_state_change_callback called")
        if callback not in self.state_change_callbacks:
            self.state_change_callbacks.append(callback)

    def remove_state_change_callback(self, callback):
        """Remove a state change callback."""
        self._debug_log(f"remove_state_change_callback called")
        if callback in self.state_change_callbacks:
            self.state_change_callbacks.remove(callback)

    def _handle_completion(self, previous_mode=None):
        """Called when a cycle ends."""
        previous_mode = previous_mode or self.timer.current_mode
        elapsed_minutes = self.timer.get_elapsed_minutes()

        self._debug_log(f"_handle_completion called, previous_mode={previous_mode}, elapsed_minutes={elapsed_minutes}")

        if previous_mode == "Focus Round":
            self.persistence_manager.log_focus_round(elapsed_minutes)

        self.timer.next_mode()

        # Notify all subscribers
        for callback in self.mode_complete_callbacks:
            try:
                callback(previous_mode)
            except Exception as e:
                self._debug_log(f"Error in mode complete callback: {e}")

        self._check_and_notify_state_change()

    def get_full_time(self):
        """
        Returns the full time for the current mode.
        """
        self._debug_log("get_full_time called")
        if self.timer.current_mode == "Focus Round":
            return self.timer.focus_round_duration
        elif self.timer.current_mode == "Recharge":
            return self.timer.recharge
        elif self.timer.current_mode == "Extended Recharge":
            return self.timer.big_recharge
        return 0  # Fallback

    def _check_and_notify_state_change(self):
        """Detects meaningful state changes and triggers callbacks."""
        self._debug_log("_check_and_notify_state_change called")
        state = self.get_state()
        comparable_state = {
            "running": state["running"],
            "mode": state["mode"],
            "current_focus_rounds": state["current_focus_rounds"],
        }
        if comparable_state != self._last_comparable_state:
            self._last_comparable_state = comparable_state
            # Notify all subscribers
            for callback in self.state_change_callbacks:
                try:
                    callback(state)
                except Exception as e:
                    self._debug_log(f"Error in state change callback: {e}")
