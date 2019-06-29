import time
import uos
from machine import I2C, Pin
#from machine import Pin

#OUT_DATA = 4
#OUT_CLOCK = 12
#OUT_LATCH = 13

#IN_LOAD = 14
#IN_CLOCK = 15
#IN_DATA = 34
#IN_ENABLE = 16

#PULSE_WIDTH_US = 1

KEYS = [
    'esc', # 0
    ['1', '!'], # 1
    ['2', '@'], # 2
    ['3', '#'], # 3
    ['4', '$'], # 4
    ['5', '%'], # 5
    ['6', '^'], # 6
    ['7', '&'], # 7
    ['8', '*'], # 8
    ['9', '('], # 9
    ['0', ')'], # 10
    ['-', '_'], # 11
    ['=', '+'], # 12
    'backspace', # 13
    None, # 14
    None, # 15
    'tab', # 16
    'q', # 17
    'w', # 18
    'e', # 19
    'r', # 20
    't', # 21
    'y', # 22
    'u', # 23
    'i', # 24
    'o', # 25
    'p', # 26
    ['[', '{'], # 27
    [']', '}'], # 28
    'enter', # 29
    None, # 30
    None, # 31
    'a', # 32
    's', # 33
    'd', # 34
    'f', # 35
    'g', # 36
    'h', # 37
    'j', # 38
    'k', # 39
    'l', # 40
    [';', ':'], # 41
    ['\'', '"'], # 42
    ['\\', '|'], # 43
    'm', # 44
    [',', '<'], # 45
    ['.', '>'], # 46
    ['/', '?'], # 47
    'shift', # 48
    ['`', '~'], # 49
    'z', # 50
    'x', # 51
    'c', # 52
    'v', # 53
    'b', # 54
    'n', # 55
    'ctrl', # 56
    'alt', # 57
    'apple', # 58
    'space', # 59
    'left', # 60
    'up', # 61
    'down', # 62
    'right' # 63
]

NAMED = {
    'left': 2, # ctrl-b
    'right': 6, # ctrl-f
    'up': 16, # ctrl-p
    'down': 14, # ctrl-n
    'tab': 9,
    'space': 32,
    'backspace': 8,
    'enter': 13 # 10
    #'escape': 27 # skip for now as it implies other things
}

MODIFIERS = {
    'shift': True,
    'ctrl': True,
    'alt': True,
    'apple': True
}

CTRLABLE = {
    'a': True,
    'b': True,
    'c': True,
    'd': True,
    'e': True,
    'f': True,
    'k': True,
    'n': True,
    'p': True,
    'u': True
}

#def shiftout_one(data, clock, latch, bit):
#    latch.value(0)
#
#    for i in range(8):
#        clock.value(0)
#        if 7-i == bit:
#            data.value(1)
#        else:
#            data.value(0)
#        clock.value(1)
#        time.sleep_us(PULSE_WIDTH_US)
#
#    latch.value(1)
#    time.sleep_us(PULSE_WIDTH_US)
#
#def shiftin(load, clock, data, enable):
#    enable.value(1)
#    load.value(0)
#    time.sleep_us(PULSE_WIDTH_US)
#    load.value(1)
#    enable.value(0)
#
#    byte = 0
#
#    for i in range(8):
#        bit = data.value()
#
#        if bit:
#            byte = byte | 1 << i
#
#        clock.value(1)
#        time.sleep_us(PULSE_WIDTH_US)
#        clock.value(0)
#
#    return byte


def ctrlify(chars):
    transformed = []
    for char in chars:
        if char in CTRLABLE:
            transformed.append(ord(char) - ord('a') + 1)
        # ignore other characters because we don't support CTRL-whatever yet
    return transformed

def shiftify(chars, index):
    transformed = []

    for char in chars:
        if isinstance(char, str):
            if len(char) == 1 and char >= 'a' and char <= 'z':
                # normal letter so uppercase or lowercase
                transformed.append(char.upper() if index else char)
            elif char in NAMED:
                # any special char
                transformed.append(NAMED[char])
            # skip others for now
        else:
            # number or punctuation so pick the first or second
            transformed.append(char[index])

    return transformed

def name_keys(keys):
    modifiers = {}
    chars = []

    for key in keys:
        name = KEYS[key]
        if name in MODIFIERS:
            modifiers[name] = True
        else:
            chars.append(name)

    # alt and apple should just ignore chars for now
    if 'alt' in modifiers or 'apple' in modifiers:
        return [modifiers, []]

    # ctrl should transform some chars and ignore the rest
    if 'ctrl' in modifiers:
        return [modifiers, ctrlify(chars)]

    # shift should transform most chars
    return [modifiers, shiftify(chars, 1 if 'shift' in modifiers else 0)]


prevKeys = None

class Keyboard:
    def __init__(self):
        #self.out_data = Pin(OUT_DATA, Pin.OUT)
        #self.out_clock = Pin(OUT_CLOCK, Pin.OUT)
        #self.out_latch = Pin(OUT_LATCH, Pin.OUT)

        #self.in_load = Pin(IN_LOAD, Pin.OUT)
        #self.in_clock = Pin(IN_CLOCK, Pin.OUT)
        #self.in_data = Pin(IN_DATA, Pin.IN)
        #self.in_enable = Pin(IN_ENABLE, Pin.OUT)

        self.i2c = I2C(scl=Pin(22), sda=Pin(21), freq=100000)

        self.prev_keys = None

        self.buffered_keys = []

    def poll(self):
        #start = time.ticks_us()
        keys = []

        numbers = [int(byte) for byte in self.i2c.readfrom(8, 8)]
        for i in range(8):
            number = numbers[i]
            if not number:
                continue
            for j in range(8):
                if number & (1 << j):
                    keys.append(8*i + j)

#        for i in range(8):
#            shiftout_one(self.out_data, self.out_clock, self.out_latch, i)
#            byte = shiftin(self.in_load, self.in_clock, self.in_data, self.in_enable)
#
#            if not byte:
#                continue
#
#            for j in range(8):
#                if byte & (1 << 7-j):
#                    keys.append(8*i + j)

        if keys == self.prev_keys:
            return

        self.prev_keys = keys

        if not len(keys):
            return

        modifiers, names = name_keys(keys)
        if not len(names):
            return

        for name in names:
            self.buffered_keys.append(ord(name) if isinstance(name, str) else name)

        #uos.dupterm_notify(screen) # TODO: dodgy
        return len(names)

        #print(keys, modifiers, names, time.ticks_diff(time.ticks_us(),start))
        # TODO: now push the keys somewhere and return True so we know to notify dupterm?

    def readinto(self, buf):
        if not len(self.buffered_keys):
            return None

        buf[0] = self.buffered_keys.pop(0)
        return 1

