import win32gui
import win32process

titles = {}


def each_window(hwnd, args):
    if win32gui.IsWindow(hwnd):
        text = win32gui.GetWindowText(hwnd)
        pid = win32process.GetWindowThreadProcessId(hwnd)
        print(text, pid)
        titles[text] = pid


win32gui.EnumWindows(each_window, 0)

print(titles)