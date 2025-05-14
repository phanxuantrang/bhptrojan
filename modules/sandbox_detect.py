import ctypes  # Import ctypes for Windows API interaction
import random  # Import random for generating random thresholds
import time  # Import time for timestamp calculations
import sys  # Import sys for system exit functionality

# Load Windows DLLs for user and kernel operations
user32 = ctypes.windll.user32  # User32.dll for input-related functions
kernel32 = ctypes.windll.kernel32  # Kernel32.dll for system uptime

# Initialize global counters for user input
keystrokes = 0  # Counter for keyboard presses
mouse_clicks = 0  # Counter for mouse clicks
double_clicks = 0  # Counter for double-click events


class LASTINPUTINFO(ctypes.Structure):
    """
    Defines the structure for storing last input information.
    """
    _fields_ = [
        ("cbSize", ctypes.c_uint),  # Size of the structure
        ("dwTime", ctypes.c_ulong)  # Timestamp of last input event
    ]


def get_last_input():
    """
    Retrieves the time elapsed since the last user input event.
    """
    struct_lastinputinfo = LASTINPUTINFO()  # Create instance of LASTINPUTINFO
    struct_lastinputinfo.cbSize = ctypes.sizeof(LASTINPUTINFO)  # Set structure size

    # Get the last input event information
    user32.GetLastInputInfo(ctypes.byref(struct_lastinputinfo))

    # Get system uptime in milliseconds
    run_time = kernel32.GetTickCount()
    elapsed = run_time - struct_lastinputinfo.dwTime  # Calculate time since last input
    print("[*] It's been %d milliseconds since the last input event." % elapsed)
    return elapsed


def get_key_press():
    """
    Detects key presses or mouse clicks and updates global counters.
    Returns the current timestamp if an event is detected, else None.
    """
    global mouse_clicks
    global keystrokes

    # Check all possible virtual key codes (0 to 255)
    for i in range(0, 0xff):
        if user32.GetAsyncKeyState(i) == -32767:  # Check if key is pressed
            # 0x1 corresponds to left mouse button
            if i == 1:
                mouse_clicks += 1  # Increment mouse click counter
                return time.time()  # Return current timestamp
            else:
                keystrokes += 1  # Increment keystroke counter
    return None


def detect_sandbox():
    """
    Detects if the program is running in a sandbox by analyzing user input patterns.
    Exits if suspicious behavior (e.g., lack of input or rapid clicks) is detected.
    """
    global mouse_clicks
    global keystrokes

    # Set random thresholds for input detection
    max_keystrokes = random.randint(10, 25)  # Random max keystrokes
    max_mouse_clicks = random.randint(5, 25)  # Random max mouse clicks

    double_clicks = 0  # Counter for double-click events
    max_double_clicks = 10  # Maximum allowed double-clicks
    double_click_threshold = 0.250  # Time threshold for double-click (in seconds)
    first_double_click = None  # Timestamp of first double-click

    max_input_threshold = 30000  # Max idle time before exiting (in milliseconds)

    previous_timestamp = None  # Timestamp of previous input event
    detection_complete = False  # Flag to control detection loop

    # Check initial idle time
    last_input = get_last_input()

    # Exit if system has been idle too long (indicative of a sandbox)
    if last_input >= max_input_threshold:
        sys.exit(0)

    # Main detection loop
    while not detection_complete:
        keypress_time = get_key_press()  # Check for new input events
        if keypress_time is not None and previous_timestamp is not None:
            # Calculate time between consecutive inputs
            elapsed = keypress_time - previous_timestamp

            # Detect double-click if inputs are within threshold
            if elapsed <= double_click_threshold:
                double_clicks += 1

                if first_double_click is None:
                    # Record timestamp of first double-click
                    first_double_click = time.time()
                else:
                    # Check for rapid succession of double-clicks (sandbox behavior)
                    if double_clicks == max_double_clicks:
                        if keypress_time - first_double_click <= (
                                max_double_clicks * double_click_threshold):
                            sys.exit(0)  # Exit if clicks are too rapid

            # Check if enough legitimate input has been detected
            if (keystrokes >= max_keystrokes
                    and double_clicks >= max_double_clicks
                    and mouse_clicks >= max_mouse_clicks):
                return  # Exit function if input thresholds are met

            previous_timestamp = keypress_time  # Update previous timestamp

        elif keypress_time is not None:
            previous_timestamp = keypress_time  # Set initial timestamp


# Run the sandbox detection
detect_sandbox()
print("We are ok!")  # Print confirmation if detection passes
