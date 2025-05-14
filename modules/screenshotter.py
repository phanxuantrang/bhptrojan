import win32gui  # Import win32gui for window handling
import win32ui  # Import win32ui for device context and bitmap operations
import win32con  # Import win32con for Windows constants
import win32api  # Import win32api for system metrics and API calls

# Get a handle to the main desktop window
hdesktop = win32gui.GetDesktopWindow()

# Determine the size and position of the virtual screen (all monitors)
width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)  # Total width of virtual screen
height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)  # Total height of virtual screen
left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)  # Leftmost coordinate of virtual screen
top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)  # Topmost coordinate of virtual screen

# Create a device context for the desktop
desktop_dc = win32gui.GetWindowDC(hdesktop)  # Get device context handle for desktop
img_dc = win32ui.CreateDCFromHandle(desktop_dc)  # Create a PyCDC object from the handle

# Create a memory-based device context
mem_dc = img_dc.CreateCompatibleDC()  # Create a compatible memory device context

# Create a bitmap object for the screenshot
screenshot = win32ui.CreateBitmap()  # Initialize a bitmap object
screenshot.CreateCompatibleBitmap(img_dc, width, height)  # Create bitmap compatible with device context
mem_dc.SelectObject(screenshot)  # Select the bitmap into the memory device context

# Copy the screen content into the memory device context
mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)  # Blit screen to memory DC

# Save the bitmap to a file
screenshot.SaveBitmapFile(mem_dc, 'c:\\WINDOWS\\Temp\\screenshot.bmp')  # Save screenshot as BMP file

# Clean up resources
mem_dc.DeleteDC()  # Delete the memory device context
win32gui.DeleteObject(screenshot.GetHandle())  # Free the bitmap object
