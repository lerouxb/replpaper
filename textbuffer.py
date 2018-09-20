try:
    import ujson
except:
    import json as ujson

ESCAPE = '\x1b'
BACKSPACE = '\b'
CR = '\r'
LF = '\n'
VT100_SINGLE_CHARS = '=>NODME78Hc'
VT52_SINGLE_CHARS = '<=>FGABCDHIKJZ'
MAX_ESCAPE_STRING = 10

#def debug(obj):
#    with open('debug.json', 'wa') as debugfile:
#        debugfile.write(ujson.dumps(obj) + '\n')

class UnknownEscapeEnding(Exception):
    pass

class UnsupportedEscapeSequence(Exception):
    pass

class UnknownCharacter(Exception):
    pass

class TooLongLine(Exception):
    pass

class OffsetNotFound(Exception):
    pass

class TooLongEscapeString(Exception):
    pass

def wrap_line(line, cols):
    """
    Return an array of line parts, each no longer than cols
    """

    split = [line[i:i + cols] for i in range(0, len(line), cols)]

    # prevent off-by-one if the line length is an exact multiple of cols
    if len(line) % cols == 0:
        split.append('')

    return split

def find_x_in_wrapped_line(offset, wrapped_line, cols):
    total = 0
    previous_total = 0
    for part in wrapped_line:
        total += len(part)
        if total >= offset:
            difference = offset - previous_total
            # prevent off-by-one if the line length is an exact multiple of cols
            if difference == cols:
                return 0
            else:
                return difference
        previous_total = total

def find_y_in_wrapped_line(offset, wrapped_line, cols):
    # it is possible that the line wraps but the cursor is not on the last part of it
    total = 0
    for index, part in enumerate(wrapped_line):
        total += len(part)
        if total >= offset:
            # prevent off-by-one if the last line is as long as cols.
            if total == offset and len(part) == cols:
                # Cursor should be on the next line which should be blank
                continue
            return index

    raise OffsetNotFound(offset)

def find_number_of_lines_on_screen(wrapped, rows):
    # optimisation for the most common case - you can't have more lines on the screen than the number of lines that will fit
    if len(wrapped) >= rows:
        return rows

    # slow path: count all the wrapped lines in the scrollback buffer
    total = 0
    for wrapped_line in wrapped:
        total += len(wrapped_line)
        # optimisation: stop once we know there are at least as many lines as will fit
        if total >= rows:
            return rows

    # rarest case is where there aren't enough lines to fill the screen yet
    return total

def calculate_row(offset, wrapped, cols, rows):
    # we're always in the last line, but not necessarily in the last wrapped part of that
    last_wrapped = wrapped[-1]

    if len(last_wrapped) > rows:
        # we don't support lines that wrap so much that it doesn't even fit on the screen
        raise TooLongLine(last_wrapped)

    relative_y = find_y_in_wrapped_line(offset, last_wrapped, cols)
    from_end = len(last_wrapped) - relative_y

    number_on_screen = find_number_of_lines_on_screen(wrapped, rows)

    return number_on_screen - from_end

def is_letter(char):
    return char >= 'A' and char <= 'z' or char >= 'a' and char <= 'z'

def is_number(char):
    return char >= '0' and char <= '9'

def is_escape_end(escape_string):
    first = escape_string[0]
    char = escape_string[len(escape_string) - 1]

    if len(escape_string) == 1:
        return first in VT100_SINGLE_CHARS
    elif first == '[':
        return is_letter(char)
    elif first == '(' or first == ')':
        return is_letter(char) or is_number(char)
    elif first == '#':
        return len(escape_string) == 2
    elif is_number(first):
        return is_letter(char)
    else:
        # If it didn't start with something that looks like the start of an escape sequence, then we're in uncharted territory.
        raise UnknownEscapeEnding(escape_string)

class Mark:
    def __init__(self, textbuffer):
        self.textbuffer = textbuffer
        self.before_length = len(textbuffer.wrapped[-1])
        self.before_y = textbuffer.y()

    def apply(self):
        after_length = len(self.textbuffer.wrapped[-1])
        if after_length == self.before_length:
            after_y = self.textbuffer.y()
            self.textbuffer.dirty.add(self.before_y)
            self.textbuffer.dirty.add(after_y)
        else:
            # this can be optimised so it doesn't redraw the entire screen every time a new line appears, but that will only help in cases where it doesn't scroll yet
            for y in range(self.textbuffer.rows):
                self.textbuffer.dirty.add(y)

class TextBuffer:
    def __init__(self, cols, rows, lines=None): # 37x16
        self.cols = cols
        self.rows = rows
        self.lines = lines[:] if lines else []
        self.wrapped = [] # array of arrays. indexes correspond with lines, array in there contains the wrapped parts

        # always at least one
        if len(self.lines) == 0:
            self.lines.append('')

        for line in self.lines:
            self.wrapped.append(wrap_line(line, self.cols))

        # since we're always editing the last line we only have to store the offset into that line. x and y can be calculated from there
        self.offset = 0
        self.dirty = set() # row numbers that are dirty (including cursor row)

        self.previous_char = None
        self.escape_string = None

    def x(self):
        return find_x_in_wrapped_line(self.offset, self.wrapped[-1], self.cols)

    def y(self):
        return calculate_row(self.offset, self.wrapped, self.cols, self.rows)

    def line(self):
        return self.lines[-1]

    def clear(self):
        self.lines = []
        self.wrapped = []
        self.offset = 0

        self.lines.append('')

        for line in self.lines:
            self.wrapped.append(wrap_line(line, self.cols))

        for y in range(self.rows):
            self.dirty.add(y)

    def start_change(self):
        return Mark(self)

    def change(self, line, apply_mark=True):
        mark = self.start_change()

        self.lines[-1] = line
        self.wrapped[-1] = wrap_line(line, self.cols)

        if apply_mark:
            mark.apply()

        return mark # so we can apply it ourselves in case of apply_mark == False

    def write(self, text):
        """
        parse text, update lines, wrapped and cursor position

        \b backspace should move the cursor back one
        \x1b[%uD  should move the cursor %u chars left
        \x1b[K clear the line from the cursor right
        \r\n new line (\r x=0, \n y+=1)
        """

        for char in text:
            self.write_char(char)

    def write_char(self, str_or_int):
        if isinstance(str_or_int, str):
            char = str_or_int
            dec = ord(str_or_int)
        else:
            char = chr(str_or_int)
            dec = str_or_int

        if self.escape_string != None:
            self.escape_string.append(char)

            if len(self.escape_string) > MAX_ESCAPE_STRING:
                raise TooLongEscapeString(self.escape_string)

            if is_escape_end(self.escape_string):
                self.handle_escape_string(self.escape_string)
                self.escape_string = None

        elif char == ESCAPE:
            self.escape_string = []
        elif char == BACKSPACE:
            self.handle_backspace()
        elif char == CR:
            self.handle_cr()
        elif char == LF:
            self.handle_lf(self.previous_char)
        elif dec < 32 or dec > 126:
            raise UnknownCharacter(char)
        else:
            self.handle_visible(char)

        self.previous_char = char

    def handle_escape_string(self, escape_string):
        first = escape_string[0]
        last = escape_string[len(escape_string) - 1]
        if first == '[':
            if len(escape_string) == 2 and last == 'K':
                return self.clear_line_from_cursor()
            if last == 'D':
                num_chars = int(''.join(escape_string[1:-1]))
                return self.move_cursor_left(num_chars)

        # we don't handle any others yet
        raise UnsupportedEscapeSequence(escape_string)

    def clear_line_from_cursor(self):
        line = self.line()
        self.change(line[:self.offset])

    def move_cursor_left(self, num_chars):
        mark = self.start_change()
        self.offset = max(self.offset - num_chars, 0)
        mark.apply()

    def handle_backspace(self):
        self.move_cursor_left(1)

    def handle_cr(self):
        # don't handle CR outside of CRLF for now
        pass

    def handle_lf(self, previous):
        # could be CRLF or LF

        old_y = self.y()

        # CR
        self.offset = 0
        # current line is dirty because the cursor is no longer there
        self.dirty.add(old_y)

        # LF
        self.lines.append('')
        self.wrapped.append([''])

        if old_y < self.rows - 1:
            # new line is dirty
            self.dirty.add(old_y + 1)
        else:
            #debug({
            #    "scrolling": True,
            #    "rows": range(self.rows)
            #})

            # no room for the new line, we have to scroll, so the whole buffer is dirty
            for y in range(self.rows):
                self.dirty.add(y)

            # trim lines and wrapped
            self.lines = self.lines[-self.rows:]
            self.wrapped = self.wrapped[-self.rows:]

    def handle_visible(self, char):
        # insert/overwrite the char at the cursor
        line = self.line()
        mark = self.change(line[:self.offset] + char + line[self.offset+1:], False)

        # move the cursor
        self.offset += 1

        # mark as dirty whatever is necessary
        mark.apply()

    def get_screen_lines(self):
        screen_lines = []
        for wrapped_lines in reversed(self.wrapped):
            for wrapped_line in reversed(wrapped_lines):
                screen_lines.append(wrapped_line)
                if len(screen_lines) == self.rows:
                    break
            if len(screen_lines) == self.rows:
                break
        screen_lines.reverse()
        return screen_lines

    def pop(self):
        """
        Return dirty lines and reset it.
        """

        # get the lines that make up the screen
        screen_lines = self.get_screen_lines()

        # pull out the dirty lines into line_dict, dict key is the line number
        line_dict = {}
        for y in self.dirty:
            if len(screen_lines) > y:
                line_dict[y] = screen_lines[y]
            else:
                line_dict[y] = ''

        #debug({
        #    "dirty": self.dirty,
        #    "screen_lines": screen_lines,
        #    "line_dict": line_dict
        #})

        self.dirty = set()

        return line_dict

