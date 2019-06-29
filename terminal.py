import micropython
import time
from uio import IOBase
import uos
from keyboard import Keyboard
from screen import Screen
from machine import Timer

# don't draw after every single character/chunk we receive. debounce instead
DEBOUNCE_PERIOD = 300

class Terminal(IOBase):
    def __init__(self):
        super().__init__()

        self.keyboard = Keyboard()
        self.screen = Screen()

        self.poller = Timer(-1)

        self.poll_ref = self.poll
        self.schedule_poll_ref = self.schedule_poll
        self.screen_write_ref = self.screen.write

    def readinto(self, buf):
        return self.keyboard.readinto(buf)

    def write(self, byteslike):
        self.screen.write(byteslike)

    def poll(self, ignore=None):
        if self.keyboard.poll():
            uos.dupterm_notify(self)

        if self.screen.last_change:
            if time.ticks_diff(time.ticks_ms(), self.screen.last_change) > DEBOUNCE_PERIOD:
                self.screen.update_screen()

        self.poller.init(period=10, mode=Timer.ONE_SHOT, callback=self.schedule_poll_ref)

    def schedule_poll(self, ignore=None):
        micropython.schedule(self.poll_ref, 0)

    def install(self):
        micropython.alloc_emergency_exception_buf(100)
        self.screen.running = True
        uos.dupterm(self)
        self.poller.init(period=10, mode=Timer.ONE_SHOT, callback=self.schedule_poll_ref)

    def uninstall(self):
        self.screen.running = False
        uos.dupterm(None)
        self.screen.clear_screen()
        self.screen.clear()

terminal = Terminal()
terminal.install()
