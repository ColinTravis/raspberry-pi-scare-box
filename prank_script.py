#!/usr/bin/env python3

import time
import random
import subprocess
import os
import signal

# --- Configuration ---
STATIC_VIDEO_PATH = "/home/admin/prank_files/static_loop.mp4"
SPOOKY_IMAGE_PATH = "/home/admin/prank_files/spooky_image.jpg" # Or .png etc.

# Timings
MIN_INITIAL_WAIT = 30 * 60   # Minimum time before first event (e.g., 45 mins)
MAX_INITIAL_WAIT = 45 * 60   # Maximum time before first event (e.g., 90 mins)

STATIC_ON_DURATION = 10      # How long static video stays visible (e.g., 30 secs)
SPOOKY_ON_DURATION = 5      # How long spooky image stays visible (e.g., 20 secs)

# --- Sleep Durations ---
MIN_SLEEP_AFTER_STATIC_1 = 5 * 60  # Min sleep time after FIRST static (e.g., 20 mins)
MAX_SLEEP_AFTER_STATIC_1 = 15 * 60  # Max sleep time after FIRST static (e.g., 40 mins)

MIN_SLEEP_AFTER_STATIC_2 = 15 * 60  # Min sleep time after SECOND static (before spooky) (e.g., 25 mins)
MAX_SLEEP_AFTER_STATIC_2 = 20 * 60  # Max sleep time after SECOND static (before spooky) (e.g., 50 mins)
# --- End Sleep Durations ---

MIN_LOOP_WAIT = 1 * 60      # Minimum time after spooky event before looping whole cycle (e.g., 45 mins)
MAX_LOOP_WAIT = 2 * 60      # Maximum time after spooky event before looping whole cycle (e.g., 90 mins)

CEC_DEVICE = "0" # 0 for TV
CEC_COMMAND_DELAY = 5 # Seconds to wait after each CEC command for TV reaction
# --- End Configuration ---

# --- Helper Functions ---
# (run_cec_command, tv_on, tv_off, kill_process)
def run_cec_command(command):
    try:
        full_command = f"echo '{command} {CEC_DEVICE}' | cec-client -s -d 1"
        print(f"Running CEC: {full_command}")
        subprocess.run(full_command, shell=True, check=True, timeout=10)
        print("CEC command sent.")
        time.sleep(CEC_COMMAND_DELAY) # Give TV time to react
    except subprocess.CalledProcessError as e:
        print(f"Error running CEC command '{command}': {e}")
    except subprocess.TimeoutExpired:
        print(f"CEC command '{command}' timed out.")

def tv_on():
    """Turns the TV on and sets active source."""
    run_cec_command("on")
    run_cec_command("as") # Set active source

def tv_off():
    """Turns the TV off (standby)."""
    run_cec_command("standby")

def kill_process(process):
    """Attempts to terminate a process gracefully, then forcefully."""
    if process and process.poll() is None: # Check if process is running
        print(f"Attempting to terminate process PID: {process.pid}")
        try:
            process.terminate()
            process.wait(timeout=5)
            print(f"Process {process.pid} terminated.")
        except subprocess.TimeoutExpired:
            print(f"Process {process.pid} did not terminate gracefully, sending SIGKILL.")
            process.kill()
            process.wait()
            print(f"Process {process.pid} killed.")
        except Exception as e:
             print(f"Error terminating process {process.pid}: {e}")

# --- Media Functions using mpv (Video/Image Only) ---
def play_static_mpv():
    """Plays static video fullscreen @ 1080p using mpv."""
    print(f"Playing static with mpv (scaled to 1080p): {STATIC_VIDEO_PATH}")
    command = [
        "mpv",
        "--vo=drm",
        "--fullscreen",
        "--loop", # or --loop-file=inf
        "--no-osd-bar",
        "--osd-level=0",
        "--really-quiet",
        "--vf=scale=1920:1080", # Force 1080p scaling
        STATIC_VIDEO_PATH
    ]
    try:
        process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Static video (mpv) started (PID: {process.pid}).")
        return process
    except Exception as e:
        print(f"Error starting static video with mpv: {e}")
        return None

def show_spooky_image_mpv():
    """Displays spooky image using mpv."""
    print(f"Showing spooky image with mpv: {SPOOKY_IMAGE_PATH}")
    img_command = [
        "mpv",
        "--vo=drm",
        "--fullscreen",
        "--no-osd-bar",
        "--osd-level=0",
        "--really-quiet",
        "--image-display-duration=inf",
        SPOOKY_IMAGE_PATH
    ]
    try:
        img_process = subprocess.Popen(img_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Spooky image (mpv) started (PID: {img_process.pid}).")
        return img_process
    except Exception as e:
        print(f"Error starting spooky image with mpv: {e}")
        return None

# --- Main Loop ---
print("Prank script starting (Static x2 -> Spooky -> Repeat).")
print(f"Static video: {STATIC_VIDEO_PATH}")
print(f"Spooky image: {SPOOKY_IMAGE_PATH}")

initial_delay = random.uniform(MIN_INITIAL_WAIT, MAX_INITIAL_WAIT)
print(f"Initial wait: {initial_delay:.2f} seconds...")
time.sleep(initial_delay)

try:
    while True:
        # --- Static Phase 1 ---
        print("\n--- Starting Static Phase 1 ---")
        static_proc_1 = play_static_mpv()
        if static_proc_1:
            print("Static video 1 process started. Turning TV on...")
            tv_on()
            print(f"Static video 1 playing for {STATIC_ON_DURATION} seconds...")
            time.sleep(STATIC_ON_DURATION)
            print("Static video 1 duration ended.")
            tv_off()
            print("TV turned off after static video 1 duration.")
            kill_process(static_proc_1)
        else:
            print("Failed to start static video 1 process.")

        # --- Sleep Phase 1 ---
        sleep_duration_1 = random.uniform(MIN_SLEEP_AFTER_STATIC_1, MAX_SLEEP_AFTER_STATIC_1)
        print(f"Sleeping for {sleep_duration_1:.2f} seconds (after static 1)...")
        time.sleep(sleep_duration_1)

        # --- Static Phase 2 ---
        print("\n--- Starting Static Phase 2 ---")
        static_proc_2 = play_static_mpv()
        if static_proc_2:
            print("Static video 2 process started. Turning TV on...")
            tv_on()
            print(f"Static video 2 playing for {STATIC_ON_DURATION} seconds...")
            time.sleep(STATIC_ON_DURATION)
            print("Static video 2 duration ended.")
            tv_off()
            print("TV turned off after static video 2 duration.")
            kill_process(static_proc_2)
        else:
            print("Failed to start static video 2 process.")

        # --- Sleep Phase 2 ---
        sleep_duration_2 = random.uniform(MIN_SLEEP_AFTER_STATIC_2, MAX_SLEEP_AFTER_STATIC_2)
        print(f"Sleeping for {sleep_duration_2:.2f} seconds (after static 2)...")
        time.sleep(sleep_duration_2)

        # --- Spooky Phase ---
        print("\n--- Starting Spooky Phase ---")
        img_proc = show_spooky_image_mpv()
        if img_proc:
            print("Image process started. Turning TV on...")
            tv_on()
            print(f"Spooky image showing for {SPOOKY_ON_DURATION} seconds...")
            time.sleep(SPOOKY_ON_DURATION)
            print("Spooky duration ended.")
            tv_off()
            print("TV turned off after spooky image duration.")
            kill_process(img_proc)
        else:
            print("Failed to start spooky image process.")

        # --- Wait Before Looping Entire Cycle ---
        loop_wait_duration = random.uniform(MIN_LOOP_WAIT, MAX_LOOP_WAIT)
        print(f"\nCycle finished. Waiting {loop_wait_duration:.2f} seconds before starting Static Phase 1 again...")
        time.sleep(loop_wait_duration)

except KeyboardInterrupt:
    print("\nScript interrupted by user. Cleaning up...")
    subprocess.run("pkill -f mpv", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        print("Attempting to turn TV off on exit...")
        tv_off()
    except Exception as cec_err:
        print(f"Could not turn TV off during cleanup: {cec_err}")
    print("Cleanup attempt finished. Exiting.")
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")
    print("Attempting cleanup...")
    subprocess.run("pkill -f mpv", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        print("Attempting to turn TV off on error exit...")
        tv_off()
    except Exception as cec_err:
        print(f"Could not turn TV off during error cleanup: {cec_err}")
    print("Exiting due to error.")
