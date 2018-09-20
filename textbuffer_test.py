import pytest
from textbuffer import *

KNOWN_ESCAPE_SEQUENCES = [

    # special vars Line, Value, Column are all positive ints

    ['Esc[20h', 'Set new line mode', 'LMN'],
    ['Esc[?1h', 'Set cursor key to application', 'DECCKM'],
    #['none', 'Set ANSI (versus VT52)', 'DECANM'],
    ['Esc[?3h', 'Set number of columns to 132', 'DECCOLM'],
    ['Esc[?4h', 'Set smooth scrolling', 'DECSCLM'],
    ['Esc[?5h', 'Set reverse video on screen', 'DECSCNM'],
    ['Esc[?6h', 'Set origin to relative', 'DECOM'],
    ['Esc[?7h', 'Set auto-wrap mode', 'DECAWM'],
    ['Esc[?8h', 'Set auto-repeat mode', 'DECARM'],
    ['Esc[?9h', 'Set interlacing mode', 'DECINLM'],

    ['Esc[20l', 'Set line feed mode', 'LMN'],
    ['Esc[?1l', 'Set cursor key to cursor', 'DECCKM'],
    ['Esc[?2l', 'Set VT52 (versus ANSI)', 'DECANM'],
    ['Esc[?3l', 'Set number of columns to 80', 'DECCOLM'],
    ['Esc[?4l', 'Set jump scrolling', 'DECSCLM'],
    ['Esc[?5l', 'Set normal video on screen', 'DECSCNM'],
    ['Esc[?6l', 'Set origin to absolute', 'DECOM'],
    ['Esc[?7l', 'Reset auto-wrap mode', 'DECAWM'],
    ['Esc[?8l', 'Reset auto-repeat mode', 'DECARM'],
    ['Esc[?9l', 'Reset interlacing mode', 'DECINLM'],

    ['Esc=', 'Set alternate keypad mode', 'DECKPAM'],
    ['Esc>', 'Set numeric keypad mode', 'DECKPNM'],

    ['Esc(A', 'Set United Kingdom G0 character set', 'setukg0'],
    ['Esc)A', 'Set United Kingdom G1 character set', 'setukg1'],
    ['Esc(B', 'Set United States G0 character set', 'setusg0'],
    ['Esc)B', 'Set United States G1 character set', 'setusg1'],
    ['Esc(0', 'Set G0 special chars. & line set', 'setspecg0'],
    ['Esc)0', 'Set G1 special chars. & line set', 'setspecg1'],
    ['Esc(1', 'Set G0 alternate character ROM', 'setaltg0'],
    ['Esc)1', 'Set G1 alternate character ROM', 'setaltg1'],
    ['Esc(2', 'Set G0 alt char ROM and spec. graphics', 'setaltspecg0'],
    ['Esc)2', 'Set G1 alt char ROM and spec. graphics', 'setaltspecg1'],

    ['EscN', 'Set single shift 2', 'SS2'],
    ['EscO', 'Set single shift 3', 'SS3'],

    ['Esc[m', 'Turn off character attributes', 'SGR0'],
    ['Esc[0m', 'Turn off character attributes', 'SGR0'],
    ['Esc[1m', 'Turn bold mode on', 'SGR1'],
    ['Esc[2m', 'Turn low intensity mode on', 'SGR2'],
    ['Esc[4m', 'Turn underline mode on', 'SGR4'],
    ['Esc[5m', 'Turn blinking mode on', 'SGR5'],
    ['Esc[7m', 'Turn reverse video on', 'SGR7'],
    ['Esc[8m', 'Turn invisible text mode on', 'SGR8'],

    ['Esc[Line;Liner', 'Set top and bottom lines of a window', 'DECSTBM'],

    ['Esc[ValueA', 'Move cursor up n lines', 'CUU'],
    ['Esc[ValueB', 'Move cursor down n lines', 'CUD'],
    ['Esc[ValueC', 'Move cursor right n lines', 'CUF'],
    ['Esc[ValueD', 'Move cursor left n lines', 'CUB'],
    ['Esc[H', 'Move cursor to upper left corner', 'cursorhome'],
    ['Esc[;H', 'Move cursor to upper left corner', 'cursorhome'],
    ['Esc[Line;ColumnH', 'Move cursor to screen location v,h', 'CUP'],
    ['Esc[f', 'Move cursor to upper left corner', 'hvhome'],
    ['Esc[;f', 'Move cursor to upper left corner', 'hvhome'],
    ['Esc[Line;Columnf', 'Move cursor to screen location v,h', 'CUP'],
    ['EscD', 'Move/scroll window up one line', 'IND'],
    ['EscM', 'Move/scroll window down one line', 'RI'],
    ['EscE', 'Move to next line', 'NEL'],
    ['Esc7', 'Save cursor position and attributes', 'DECSC'],
    ['Esc8', 'Restore cursor position and attributes', 'DECSC'],

    ['EscH', 'Set a tab at the current column', 'HTS'],
    ['Esc[g', 'Clear a tab at the current column', 'TBC'],
    ['Esc[0g', 'Clear a tab at the current column', 'TBC'],
    ['Esc[3g', 'Clear all tabs', 'TBC'],

    ['Esc#3', 'Double-height letters, top half', 'DECDHL'],
    ['Esc#4', 'Double-height letters, bottom half', 'DECDHL'],
    ['Esc#5', 'Single width, single height letters', 'DECSWL'],
    ['Esc#6', 'Double width, single height letters', 'DECDWL'],

    ['Esc[K', 'Clear line from cursor right', 'EL0'],
    ['Esc[0K', 'Clear line from cursor right', 'EL0'],
    ['Esc[1K', 'Clear line from cursor left', 'EL1'],
    ['Esc[2K', 'Clear entire line', 'EL2'],

    ['Esc[J', 'Clear screen from cursor down', 'ED0'],
    ['Esc[0J', 'Clear screen from cursor down', 'ED0'],
    ['Esc[1J', 'Clear screen from cursor up', 'ED1'],
    ['Esc[2J', 'Clear entire screen', 'ED2'],

    ['Esc5n', 'Device status report', 'DSR'],
    ['Esc0n', 'Response: terminal is OK', 'DSR'],
    ['Esc3n', 'Response: terminal is not OK', 'DSR'],

    ['Esc6n', 'Get cursor position', 'DSR'],
    ['EscLine;ColumnR', 'Response: cursor is at v,h', 'CPR'],

    ['Esc[c', 'Identify what terminal type', 'DA'],
    ['Esc[0c', 'Identify what terminal type (another)', 'DA'],
    ['Esc[?1;Value0c', 'Response: terminal type code n', 'DA'],

    ['Escc', 'Reset terminal to initial state', 'RIS'],

    ['Esc#8', 'Screen alignment display', 'DECALN'],
    ['Esc[2;1y', 'Confidence power up test', 'DECTST'],
    ['Esc[2;2y', 'Confidence loopback test', 'DECTST'],
    ['Esc[2;9y', 'Repeat power up test', 'DECTST'],
    ['Esc[2;10y', 'Repeat loopback test', 'DECTST'],

    ['Esc[0q', 'Turn off all four leds', 'DECLL0'],
    ['Esc[1q', 'Turn on LED #1', 'DECLL1'],
    ['Esc[2q', 'Turn on LED #2', 'DECLL2'],
    ['Esc[3q', 'Turn on LED #3', 'DECLL3'],
    ['Esc[4q', 'Turn on LED #4', 'DECLL4']
]

def replace_sequence_placeholders(sequence):
    return (sequence
        .replace('Value', '111')
        .replace('Line', '222')
        .replace('Column', '333'))

def test_known_sequence():
    for [sequence, description, name] in KNOWN_ESCAPE_SEQUENCES:
        sequence = replace_sequence_placeholders(sequence)
        chars = list(sequence[3:])
        assert is_escape_end(chars)
        if len(chars) > 1:
            assert is_escape_end(chars[:-1]) == False

def test_unknown_escape_ending():
    with pytest.raises(UnknownEscapeEnding):
        is_escape_end([' ', ' ']) # fails on the second char

def test_unknown_character():
    with pytest.raises(UnknownCharacter):
        tb = TextBuffer(16, 2)
        tb.write([0])

def test_unsupported_escape_sequence():
    with pytest.raises(UnsupportedEscapeSequence):
        tb = TextBuffer(16, 2)
        tb.write([27, ord('c')])

def test_wrap_line():
    assert wrap_line('*'*16, 16) == ['*'*16, '']
    assert wrap_line('*'*17, 16) == ['*'*16, '*']
    assert wrap_line('*'*32, 16) == ['*'*16, '*'*16, '']

def test_offset_not_found():
    with pytest.raises(OffsetNotFound):
        find_y_in_wrapped_line(100, [], 16)

def test_line_too_long():
    with pytest.raises(TooLongLine):
        # 32-character long line on a 16x2 screen should throw
        calculate_row(100, [['*'*16, '*'*16, '']], 16, 2)

def test_too_long_escape_string():
    tb = TextBuffer(16, 2)
    with pytest.raises(TooLongEscapeString):
        tb.write(chr(27) + '[' + '1'*10)

# TODO: tests for find_y_in_wrapped_line

# TODO: tests for calculate_row

def test_clear_line_from_cursor_unchanged_num_lines():
    tb = TextBuffer(16, 2)
    tb.write('hello\nthere')
    tb.write('\b')
    tb.write('\b')
    line_dict = tb.pop()
    assert line_dict == { 0: 'hello', 1: 'there' }
    assert tb.offset == 3
    assert tb.x() == 3
    assert tb.y() == 1

    tb.write([27, '[', 'K'])
    line_dict = tb.pop()
    assert line_dict == { 1: 'the' }
    assert tb.offset == 3
    assert tb.x() == 3
    assert tb.y() == 1

def test_clear_line_from_cursor_changed_num_lines():
    tb = TextBuffer(16, 2)
    tb.write('*' * 20)
    tb.write([27, '[', '1', '0', 'D'])
    line_dict = tb.pop()
    assert line_dict == { 0: '*'*16, 1: '*'*4 }
    assert tb.offset == 10
    assert tb.x() == 10
    assert tb.y() == 0

    tb.write([27, '[', 'K'])
    line_dict = tb.pop()
    assert line_dict == { 0: '*'*10, 1: '' }
    assert tb.offset == 10
    assert tb.x() == 10
    assert tb.y() == 0

def test_move_cursor_left_within_line():
    tb = TextBuffer(16, 2)
    tb.write('*' * 20)
    line_dict = tb.pop()
    assert line_dict == { 0: '*'*16, 1: '*'*4 }
    assert tb.offset == 20
    assert tb.x() == 4
    assert tb.y() == 1

    tb.write([27, '[', '2', 'D'])
    line_dict = tb.pop()
    assert line_dict == { 1: '*'*4 }
    assert tb.offset == 18
    assert tb.x() == 2
    assert tb.y() == 1

def test_move_cursor_left_crossing_edge():
    tb = TextBuffer(16, 2)
    tb.write('*' * 20)
    line_dict = tb.pop()
    assert line_dict == { 0: '*'*16, 1: '*'*4 }
    assert tb.offset == 20
    assert tb.x() == 4
    assert tb.y() == 1

    tb.write([27, '[', '1', '0', 'D'])
    line_dict = tb.pop()
    assert line_dict == { 0: '*'*16, 1: '*'*4 }
    assert tb.offset == 10
    assert tb.x() == 10
    assert tb.y() == 0

def test_backspace_within_line():
    tb = TextBuffer(16, 2)
    tb.write('*' * 20)
    line_dict = tb.pop()
    assert line_dict == { 0: '*'*16, 1: '*'*4 }
    assert tb.offset == 20
    assert tb.x() == 4
    assert tb.y() == 1

    tb.write('\b')
    line_dict = tb.pop()
    assert line_dict == { 1: '*'*4 }
    assert tb.offset == 19
    assert tb.x() == 3
    assert tb.y() == 1

def test_backspace_crossing_edge():
    tb = TextBuffer(16, 2)
    tb.write('*' * 16)
    line_dict = tb.pop()
    assert line_dict == { 0: '*'*16, 1: '' }
    assert tb.offset == 16
    assert tb.x() == 0
    assert tb.y() == 1

    tb.write('\b')
    line_dict = tb.pop()
    assert line_dict == { 0: '*'*16, 1: '' }
    assert tb.offset == 15
    assert tb.x() == 15
    assert tb.y() == 0

def test_newline_without_scrolling():
    tb = TextBuffer(16, 2)
    tb.write('>>> ')
    line_dict = tb.pop()
    assert line_dict == { 0: '>>> ' }
    assert tb.offset == 4
    assert tb.x() == 4
    assert tb.y() == 0

    tb.write('\n')
    line_dict = tb.pop()
    assert line_dict == { 0: '>>> ', 1: '' }
    assert tb.offset == 0
    assert tb.x() == 0
    assert tb.y() == 1

def test_newline_with_scrolling():
    tb = TextBuffer(16, 2)
    tb.write('>>> \n')
    line_dict = tb.pop()
    assert line_dict == { 0: '>>> ', 1: '' }
    assert tb.offset == 0
    assert tb.x() == 0
    assert tb.y() == 1

    tb.write('\n')
    line_dict = tb.pop()
    assert line_dict == { 0: '', 1: '' }
    assert tb.offset == 0
    assert tb.x() == 0
    assert tb.y() == 1

def test_new_character_without_wrapping():
    tb = TextBuffer(16, 2)
    tb.write('\n')
    line_dict = tb.pop()
    assert line_dict == { 0: '', 1: '' }
    assert tb.offset == 0
    assert tb.x() == 0
    assert tb.y() == 1

    tb.write('*')
    line_dict = tb.pop()
    assert line_dict == { 1: '*' }
    assert tb.offset == 1
    assert tb.x() == 1
    assert tb.y() == 1

def test_new_character_with_wrapping_without_scrolling():
    tb = TextBuffer(16, 2)
    tb.write('*'*15)
    line_dict = tb.pop()
    assert line_dict == { 0: '*'*15 }
    assert tb.offset == 15
    assert tb.x() == 15
    assert tb.y() == 0

    tb.write('*')
    line_dict = tb.pop()
    assert line_dict == { 0: '*'*16, 1:'' }
    assert tb.offset == 16
    assert tb.x() == 0
    assert tb.y() == 1

    # once wrapped we can add more
    tb.write('*')
    line_dict = tb.pop()
    assert line_dict == { 1:'*' }
    assert tb.offset == 17
    assert tb.x() == 1
    assert tb.y() == 1

def test_new_character_with_wrapping_with_scrolling():
    tb = TextBuffer(16, 2)
    tb.write('\n' + '*'*15)
    line_dict = tb.pop()
    assert line_dict == { 0: '', 1: '*'*15 }
    assert tb.offset == 15
    assert tb.x() == 15
    assert tb.y() == 1

    tb.write('*')
    line_dict = tb.pop()
    assert line_dict == { 0: '*'*16, 1:'' }
    assert tb.offset == 16
    assert tb.x() == 0
    assert tb.y() == 1

def test_swallows_cr():
    tb = TextBuffer(16, 2)
    tb.write('\r');
    line_dict = tb.pop()
    assert line_dict == {}
    assert tb.offset == 0
    assert tb.x() == 0
    assert tb.y() == 0
