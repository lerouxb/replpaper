from utime import sleep
from textbuffer import TextBuffer
from uio import IOBase
from uos import dupterm

class Monitor(IOBase):
    def __init__(self, cols=40, rows=4):
        self.textbuffer = TextBuffer(cols, rows)

    def read(self, size):
        return None

    def write(self, byteslike):
        with open("write.txt", 'wa') as dumpfile:
            for byte in byteslike:
                dumpfile.write(str(byte) + ' ' + chr(byte) + '\n')

        self.textbuffer.write(byteslike)

        self.dump_screen()
        self.dump_lines()
        self.dump_wrapped()

        return len(byteslike)

    def dump_screen(self):
        lines = []
        line_dict = self.textbuffer.pop()
        for y in range(self.textbuffer.rows):
            if y in line_dict:
                lines.append(line_dict[y] + '\n')
            else:
                lines.append('*' * self.textbuffer.cols + '\n')

        lines.append('\n')
        lines.append(str(self.textbuffer.offset) + '\n')
        lines.append(self.textbuffer.previous_char + '\n')
        lines.append(str(len(line_dict)) + '\n')

        with open("screen.txt", 'w') as dumpfile:
            for line in lines:
                dumpfile.write(line)

    def dump_lines(self):
        with open("lines.txt", 'w') as dumpfile:
            for line in self.textbuffer.lines:
                dumpfile.write(line + '\n')

    def dump_wrapped(self):
        with open("wrapped.txt", 'w') as dumpfile:
            for wrapped_lines in self.textbuffer.wrapped:
                for line in wrapped_lines:
                    dumpfile.write(line + '\n')

monitor = Monitor()
prev = dupterm(monitor, 1)
#print(prev)
