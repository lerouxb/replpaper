# REPLPAPER

Duplicate a MicroPython REPL on an e-Paper module

MicroPython's [uos.dupterm()](http://docs.micropython.org/en/latest/unix/library/uos.html#uos.dupterm) allows you to duplicate or switch the REPL/terminal on a stream-like object.

So I implemented a stream-like object that can parse and interpret the subset of VT100 escape sequences used by MicroPython's readline, debounces input to try and batch updates, keeps track of lines and cursor position, wraps the lines, tracks which parts of the screen are dirty and efficiently updates the screen through (fast) partial updates when only part of the screen changed and (slow) full updates only when the entire screen changes.

This means you can connect to MicroPython running on a microcontroller over serial interface and the output will show up on a terminal screen in addition to your serial terminal.

This is admittedly not terribly useful yet because you still have to connect over serial to input text. The next step is to add keyboard support (probably PS/2 at first, dedicated DIY one later) and then you can have a self-contained Python REPL.

What's the point of all of that?

1) For fun.

2) You could have a modern take on 1980s style "boot to BASIC" computers, except it would be handheld. Kinda like a graphing calculator or those early 1990s PDAs. But it is also a microcontroller devkit for doing "arduino" stuff straight on it, no PC required.

3) Leave one of these in a project. By default the screen would show the normal dashboard with whatever stats and things make sense (temperature, speed, battery state of charge, relative humidity..), but then you press some key combo on the built-in PCB keyboard and drop into a debug or developer console where you can poke at whatever modules are in memory. Type `exit()` and it goes back to the dashboard as usual.

## Installation instructions

I have only tested this on an esp32-wroom module connected to a 2.9" e-Paper module from waveshare. Make sure you get the 2 colour one because it can do partial screen updates at 0.3 seconds. The 3 colour ones are very slow and can only do full updates. The larger screens unfortunately don't come in variations that have the common SPI interface and that can do fast partial updates. Except for the largest, most expensive one.

Follow the instructions on the [esp32](https://github.com/micropython/micropython/tree/master/ports/esp32) port for getting MicroPython onto the board.

Use Adafruit's excellent [ampy](https://github.com/adafruit/ampy) to upload additional modules from this repo and elsewhere to the board's internal file system.

You need epaper2in9.py (I only made very minor changes to [mcauser](https://github.com/mcauser/micropython-waveshare-epaper)'s file), textbuffer.py and screen.py. epaper2in9 is the e-ink screen driver, textbuffer manages lines of text wrapped to rows and cols for a screen with fixed with font and screen implements the stream for dupstream.

In addition to that you will need [bitfont.py](https://github.com/ShrimpingIt/bitfont/blob/master/python/bitfont.py) and [font_5x8](https://github.com/ShrimpingIt/bitfont/blob/master/python/faces/font_5x8.py) from the excellent [bitfont](https://github.com/ShrimpingIt/bitfont) library.

## Usage

Connect to the micropython board over serial as usual. I use `$ picocom -b 115200 /dev/cu.SLAB_USBtoUART`.

Then to install the screen stream, run `from screen import screen`. This will setup the screen driver, clear it and run uos.dupterm to install it. All terminal output will now appear duplicated on the e-ink screen.

To clear the screen, call `screen.clear()`.

To uninstall it you can call `screen.uninstall()`. Alternatively just reboot the esp32.

You will need to uninstall the screen or reboot if you want to use ampy to upload more modules because it uses the same serial connection to upload files and things get.. weird.

## Testing

I use [pytest](https://pytest.org/) for running the unit tests in textbuffer.py and [coverage](https://coverage.readthedocs.io/) for coverage. Via the command `coverage run --omit "*site-packages*" $(which pytest)` and then `coverage report -m` to see the report.

For discovering what MicroPython's readline is doing I wrote unix_monitor.py. It intended for use with the unix port. But you have to change the compile-time configuration of that to support uos.dupterm() because there are no slots by default. Useful to keep around in case this ever has to support more escape sequences and what not.
