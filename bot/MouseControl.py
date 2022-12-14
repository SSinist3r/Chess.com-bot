import win32api, win32con
import time

class MouseControl:

    def mousePos(self, x, y):
        win32api.SetCursorPos((x, y))


    def mouseClick(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        time.sleep(0.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
