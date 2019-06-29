import time
from machine import Pin, SPI#, Timer
from framebuf import FrameBuffer, MONO_HLSB
from textbuffer import TextBuffer
from epaper2in9 import EPD
from font_5x8 import font

screen_width = 296
screen_height = 128

font_width = 5
font_height = 8

cols = screen_width // font_width
rows = screen_height // font_height


class Screen:
    def __init__(self):

        self.textbuffer = TextBuffer(cols, rows)

        # make the framebuffer we draw into the size of one line of text as that's all we need
        self.buf = bytearray(screen_width * font_height // 8)
        # the screen defaults to portrait and we want to use it in landscape so we have to rotate as we go, unfortunately. that's why dimensions look swapped around
        self.fb = FrameBuffer(self.buf, font_height, screen_width, MONO_HLSB)

        sck = Pin(18, Pin.OUT)
        mosi = Pin(23, Pin.OUT)
        miso = Pin(19, Pin.IN)
        spi = SPI(2, baudrate=80000000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)

        cs = Pin(5, Pin.OUT)
        dc = Pin(17, Pin.OUT)
        rst = Pin(27, Pin.OUT)
        busy = Pin(35, Pin.IN)

        self.epd = EPD(spi, cs, dc, rst, busy)
        self.epd.init()

        self.clear_screen()

        # we were in slow mode for the initial clear on startup, we're now going to fast mode as that's the most likely one we'll need next
        self.mode = 'slow'
        self.set_fast()

        self.running = False

        self.last_change = None

    def write(self, byteslike):
        self.textbuffer.write(byteslike)
        self.debounce_update()

    def set_slow(self):
        if self.mode == 'slow':
            return

        self.mode = 'slow'
        self.epd.set_slow()

    def set_fast(self):
        if self.mode == 'fast':
            return

        self.mode = 'fast'
        self.epd.set_fast()

    def plot(self, x, y):
        # rotate 90 degrees on the fly
        self.fb.pixel(font_height - 1 - y, x, 0)

    def plot_inverse(self, x, y):
        # rotate 90 degrees
        self.fb.pixel(font_height - 1 - y, x, 1)

    def debounce_update(self):
        self.last_change = time.ticks_ms()

    def update_screen(self, tmr=None):
        self.last_change = None

        if not self.running:
            return

        # TODO: keep some performance stats somewhere

        # the changed lines. keys are row indexes, values are line strings
        lines_dict = self.textbuffer.pop()

        # slow update if the entire screen changed (gives it a chance to remove the ghosting), otherwise fast for partial updates
        if len(lines_dict) == self.textbuffer.rows:
            self.set_slow()
        else:
            self.set_fast()

        cursor_x = self.textbuffer.x()
        cursor_y = self.textbuffer.y()

        # keep both buffers in the display's controller in sync
        for i in range(2):
            self._update_buffer(lines_dict, cursor_x, cursor_y)

            # display only one of the buffers
            if i == 0:
                self.epd.display_frame()

    def _update_buffer(self, lines_dict, cursor_x, cursor_y):
        for row_index, line in lines_dict.items():
            # clear the framebuffer because it now represents this row
            self.fb.fill(1)

            # print the text
            font.draw_line(line.encode('ascii'), self.plot)

            if row_index == cursor_y:
                # draw the cursor (rotated 90 degrees)
                self.fb.fill_rect(0, cursor_x * font_width, font_height, font_width, 0)

                # if the cursor is on a character, also draw that character inverted
                if cursor_x < len(line):
                    font.draw_line(line[cursor_x].encode('ascii'), self.plot_inverse, cursor_x*font_width, 1)

            # copy this row to the screen's buffer (rotated 90 degrees)
            self.epd.set_frame_memory(self.buf, screen_height - ((row_index+1) * font_height), 0, font_height, screen_width)

    def clear_screen(self):
        self.fb.fill(1)

        # clear both buffers
        for i in range(2):
            for row_index in range(self.textbuffer.rows):
                self.epd.set_frame_memory(self.buf, row_index * font_height, 0, font_height, screen_width)

            # but only clear the screen once
            if i == 0:
                self.epd.display_frame()

    def clear(self):
        self.textbuffer.clear()
        self.debounce_update()

