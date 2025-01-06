#!/bin/bash

# Automatically determine the app and venv paths relative to this script
SCRIPT_DIR=$(dirname "$(realpath "$0")")
APP_PATH="$SCRIPT_DIR/src/tomatix/app/main.py"
VENV_PATH="$SCRIPT_DIR/.venv/bin/activate"
LOCK_FILE="/tmp/tomatix.lock"

# Check if the app is running
is_app_running() {
  ps -p $(cat "$LOCK_FILE" 2>/dev/null) >/dev/null 2>&1
}

stop_app() {
  if is_app_running; then
    local pid
    pid=$(cat "$LOCK_FILE")
    echo "Stopping existing Tomatix Timer (PID: $pid)..."
    kill "$pid"
  else
    echo "No running instance to stop."
  fi
}

start_app() {
  echo "Starting Tomatix Timer..."
  (
    source "$VENV_PATH"   # Activate the virtual environment in a subshell
    python3 "$APP_PATH" & # Run the app in the background
    echo $! >"$LOCK_FILE" # Save the PID to the lock file
  )
}

if [ "$1" == "restart" ]; then
  stop_app
  start_app
elif [ "$1" == "stop" ]; then
  stop_app
else
  if is_app_running; then
    echo "Tomatix Timer is already running. Use '$0 restart' to restart."
  else
    start_app
  fi
fi
