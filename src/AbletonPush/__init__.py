import threading
import mido  # https://github.com/mido/mido, also run pip3 install python-rtmidi --install-option="--no-jack"
from time import sleep
import re
from AbletonPush.constants import PUSH_TEXT_CAHRACTER_SET_DICT, PUSH_TEXT_CAHRACTER_SET_ALTERNATIVES_DICT, \
    SYSEX_PREFIX_PUSH, ButtonGridColors, ButtonGridColorsBrightness


class AbletonPush(threading.Thread):
    def __init__(self, port_user: str = "", port_live: str = "", print_midi: bool = False, test_mode: bool = False):
        """
        Init a AbletonPush object and prepare MIDI-connections.
        :type test_mode: Test-mode write control-values back so buttons light up.
        :type print_midi: Shows MIDI-messages in the console.
        :type port_live: Set MIDI IO-port for Ableton Push Port Live.
                         Port is found via a regex search of available ports.
                         Usually: Ableton Push:Ableton Push Live Port 28:0
        :type port_user: Set MIDI IO-port for Ableton Push Port User.
                         Port is found via a regex search of available ports.
                         Usually: Ableton Push:Ableton Push User Port 28:1
        """
        # Flags
        self.print_midi = print_midi
        self.test_mode = test_mode

        # Find port names
        self._ports_midi = mido.get_ioport_names()
        self.port_user = self._find_port(port_user, "Push.*User")
        self.port_live = self._find_port(port_live, "Push.*Live")

        # Instantiate variables
        self.midi_user = None
        self.midi_live = None
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.quit = False

    def run(self):
        self.midi_user = mido.open_ioport(self.port_user)
        self.midi_live = mido.open_ioport(self.port_live)
        while True:
            if self.quit:
                return
            msg = self.midi_user.receive(False)
            if msg:
                if self.test_mode:
                    if msg.type == 'note_on':
                        self._send_note_on(channel=msg.channel, note=msg.note, velocity=msg.velocity)
                    if msg.type == 'note_off':
                        self._send_note_on(channel=msg.channel, note=msg.note, velocity=0)
                    if msg.type == 'control_change':
                        if msg.value == 127:
                            self._send_control_change(channel=msg.channel, control=msg.control, value=7)
                        else:
                            self._send_control_change(channel=msg.channel, control=msg.control, value=1)
                    if msg.type == 'polytouch':
                        pass
                if self.print_midi:
                    print(f"User {msg}")
            msg = self.midi_live.receive(False)
            if msg:
                if self.print_midi:
                    print(f"Live {msg}")
            sleep(0.001)

    def _send_control_change(self, channel: int, control: int, value: int):
        """
        Send a Control-Change message to the Push.
        :param channel: int channel number 0-127
        :param control: int Control 0-127
        :param value: int Value 0-127
        """
        m = mido.Message('control_change', channel=channel, control=control, value=value)
        self.midi_user.send(m)

    def _send_note_on(self, channel: int, note: int, velocity: int):
        """
        Send a Note-On message to the Push.
        :param channel: int channel number 0-127
        :param note: int Note 0-127
        :param velocity: int Velocity 0-127
        """
        m = mido.Message('note_on', channel=channel, note=note, velocity=velocity)
        self.midi_user.send(m)

    def _send_push_sysex(self, d: list):
        """
        Send a sysex-message to the Push.
        :param d: list of bytes to send. No value can be larger than 127 due to the MIDI-standard.
        """
        m = mido.Message('sysex')
        # Prefix Manufacturer and Product ID before the message. Mido will prefix sysex-command (240) and suffix (247).
        m.data = SYSEX_PREFIX_PUSH + d
        self.midi_live.send(m)

    def _set_user_mode(self, user=True):
        """
        Set User/Live mode for Ableton Push.
        :param user: bool true for user mode, false for live mode
        """
        command = [98]
        length = [0, 1]
        d = command + length + [int(user)]
        self._send_push_sysex(d)

    def button_grid_set_color(self, pad: int = None, red: int = None, green: int = None, blue: int = None,
                              note: int = None, palette_color: int = None):
        """
        Set color on button using either R, G, B and pad number, or palette color index using pad's note-number.
        https://web.archive.org/web/20140509024845/https://cycling74.com/wiki/index.php?title=Push_Programming_Oct13_03
        https://forum.ableton.com/viewtopic.php?t=192920#p1673347
        http://pushmod.blogspot.com/2014/05/the-ableton-push-is-definitely-some.html
        :type pad: int 0-71 Pad's number, 0 i button left.
        :param red: int 0-255 red value, only applicable together with pad.
        :param green: int 0-255 green value, only applicable together with pad.
        :param blue: int 0-255 blue value, only applicable together with pad.
        :param note: int CC-note representing pad.
        :param palette_color: Index of color palette, only applicable together with note.
        """
        if pad is None and note is None:
            raise Exception("Arguments pad or note must be set when setting color.")
        if pad is not None:
            if red is None or green is None or blue is None:
                raise Exception("Arguments red, green and blue needs to be set when setting color using pad.")
            command = [4]
            length = [0, 8]
            transition_type = [0]
            r1 = int(red / 16)
            r2 = red % 16
            g1 = int(green / 16)
            g2 = green % 16
            b1 = int(blue / 16)
            b2 = blue % 16
            d = command + length + [pad] + transition_type + [r1, r2] + [g1, g2] + [b1, b2]
            self._send_push_sysex(d)
        else:
            if palette_color is None:
                raise Exception("Argument palette_color must be set when setting color using note.")
            palette_color_index = 0
            if type(palette_color) is int:
                palette_color_index = palette_color
            else:
                palette_color_index = palette_color.value
            self._send_note_on(channel=0, note=note, velocity=palette_color_index)

    def display_set_brightness(self, brightness: int):
        """
        Set display brightness.
        http://pushmod.blogspot.com/2014/05/the-ableton-push-is-definitely-some.html
        :type brightness: int 0-127
        """
        command = [124]
        length = [0, 1]
        d = command + length + [brightness]
        self._send_push_sysex(d)

    def display_set_contrast(self, contrast: int):
        """
        Set display contrast.
        http://pushmod.blogspot.com/2014/05/the-ableton-push-is-definitely-some.html
        :type contrast: int 0-127
        """
        command = [122]
        length = [0, 1]
        d = command + length + [contrast]
        self._send_push_sysex(d)

    @staticmethod
    def _convert_push_text(text: str) -> list:
        """
        Will convert a string to a list of integers that will render on the Push.
        :type text: str to convert
        """
        out = []
        for c in text:
            if isinstance(c, int):
                if 0 <= c <= 127:
                    out.append(c)
                else:
                    raise Exception(f"Integer {c} is not valid, it must be between 0 and 127.")
            else:
                if c in PUSH_TEXT_CAHRACTER_SET_DICT.keys():
                    out.append(PUSH_TEXT_CAHRACTER_SET_DICT[c])
                else:
                    if c in PUSH_TEXT_CAHRACTER_SET_ALTERNATIVES_DICT.keys():
                        out.append(PUSH_TEXT_CAHRACTER_SET_ALTERNATIVES_DICT[c])
                    else:
                        raise Exception(f"Character {c} is not valid, it must be a 7bit ASCII character.")
        return out

    def display_set_text(self, text: str, line: int = 0, offset: int = 0, column: int = None):
        """
        Set display text.
        240,71,127,21,<24+line(0-3)>,0,<Nchars+1>,<Offset>,<Chars>,247
        Each display line is divided into 4 groups of 17 characters, the offset (column) is then form 0 to 67.
        To write a string to a part of the line, an offset(column) and size needs to be passed
        (see "Write Text" SysEx message above).
        So, to write "Hello World!" to the fifth column of the second line, just send:
        240,71,127,21,25,0,13,4,"Hello World",247
        http://pushmod.blogspot.com/2014/05/the-ableton-push-is-definitely-some.html
        :type text: str Text to write 1- characters.
        :type line: int 0-3, optional
        :type offset: int, optional
        :type column: int 0-3, optional
        """
        command = [24 + line]
        length = len(text) + 1
        lengths = [int(length / 128), (length % 128)]
        if column:
            offset = 17 * column
        offset = [offset]
        chars = self._convert_push_text(text)
        d = command + lengths + offset + chars
        self._send_push_sysex(d)

    def display_clear_text(self, line: int = -1, column: int = -1, separator=" "):
        """
        Clears a line or column on the display.
        :type line: int 0-3 default will clear all
        :type column: int 0-3 default will clear all columns
        :param separator: str or int, one character
        """
        blankline = []
        width = 0
        if column == -1:
            width = 17 * 4  # Full row
            column = 0

        else:
            width = 17 * 1  # One column
        blankline = [separator] * width
        if line == -1:
            for i in range(4):
                self.display_set_text(line=i, offset=column * 17, text=blankline)
        else:
            self.display_set_text(line=line, offset=column * 17, text=blankline)

    def touch_strip_set_mode(self, mode: int = 0):
        """
        Set touch strip mode.
        240,71,127,21,99,0,1,<Mode>,247
        The touch ribbon to the left of the pads sends out pitch bend, but it also has a column of 24 LEDs which can be
        individually addressable.
        The type 99 SysEx message sets the behavior of the LED strip, I am still checking what are the options there,
        but option 4 seems to set the LED strip to "addressable" mode.
        Each 3 LEDs, from the bottom up, are addressed by one of the 8 bytes of the type 100 SysEx message.
        There are 3 possible values for each LED, off, dim and lit, and setting each byte of that SysEx message
        from 0 to 63 will allow to obtain all the combinations. Setting from 64 to 127 will just repeat
        the same sequences.
        http://pushmod.blogspot.com/2014/05/the-ableton-push-is-definitely-some.html
        :type mode: int 0-4, optional
        """
        command = [99]
        length = [0, 1]
        d = command + length + [mode]
        self._send_push_sysex(d)

    def touch_strip_set_leds(self, leds: list):
        """
        Set touch strip leds levels. Touch strip mode needs to be in addressable mode.
        240,71,127,21,100,0,8,<8xled-bytes>,247
        Each 3 LEDs, from the bottom up, are addressed by one of the 8 bytes of the type 100 SysEx message.
        There are 3 possible values for each LED, off, dim and lit, and setting each byte of that SysEx message
        from 0 to 63 will allow to obtain all the combinations. Setting from 64 to 127 will just repeat
        the same sequences.
        http://pushmod.blogspot.com/2014/05/the-ableton-push-is-definitely-some.html
        :type leds: list of 24 led-levels, bottom to top order. A level can be 0-3.
        """
        command = [100]
        length = [0, 8]
        led_bytes = [0] * 8
        if len(leds) > 24:
            raise Exception(f"Number of leds can be max 24, it's now {len(leds)}.")
        for i, led in enumerate(leds):
            if led < 0 or led > 3:
                raise Exception(f"Led level can only be 0-3. Led {i} is {led}.")
            # Pack the 24 led levels into a tightly packed 8 bytes.
            # Bit shift in by (index modula of 3) x 2. This will place modula 0 at the two lowest bits like {0b00332211}
            led_bytes[int(i / 3)] += led << ((i % 3) * 2)
        d = command + length + led_bytes
        self._send_push_sysex(d)

    def _find_port(self, port_name: str, fallback: str) -> str:
        if port_name:
            port_name_to_search = port_name
        else:
            port_name_to_search = fallback
        if not port_name_to_search.startswith(".*"):
            port_name_to_search = ".*" + port_name_to_search
        if not port_name_to_search.endswith(".*"):
            port_name_to_search += ".*"
        r = re.compile(port_name_to_search, re.IGNORECASE)
        port_matches = list(filter(r.match, self._ports_midi))
        found_port = next(iter(port_matches), None)
        if found_port:
            return found_port
        else:
            raise Exception(f"Couldn't find {port_name} in listed IO-ports {self._ports_midi}.")


if __name__ == '__main__':
    import argparse
    from pysh.shell import Pysh  # https://github.com/TimGremalm/pysh

    parser = argparse.ArgumentParser()
    parser.add_argument('--printmidi', '-p',
                        action='store_true',
                        help="Shows MIDI-messages in the console.")
    parser.add_argument('--midiportuser', "--user",
                        type=str, default="",
                        help="Set MIDI IO-port for Ableton Push Port User. "
                             "Default: Ableton Push:Ableton Push User Port 28:1")
    parser.add_argument('--midiportlive', "--live",
                        type=str, default="",
                        help="Set MIDI IO-port for Ableton Push Port Live. "
                             "Default: Ableton Push:Ableton Push Live Port 28:0")
    parser.add_argument('--shell', '-s',
                        action='store_true',
                        help='Start an interactive ipython shell where you can interact with the Ableton Push.')
    parser.add_argument('--test', '-t',
                        action='store_true',
                        help='Test-mode write control-values back so buttons light up.')
    parser.add_argument('--printports', '-l',
                        action='store_true',
                        help='Lists available MIDI IO ports.')
    args = parser.parse_args()

    # setattr(obj, name, value, /)
    # Sets the named attribute on the given object to the specified value.
    # setattr(ableton_push, "a", 42)

    print("Ableton Push")
    if args.printports:
        print("MIDI IO ports:")
        io_ports = mido.get_ioport_names()
        for port in io_ports:
            print(f"\t{port}")
        print("exit...")
    else:
        ableton_push = AbletonPush(print_midi=args.printmidi,
                                   port_live=args.midiportlive,
                                   port_user=args.midiportuser,
                                   test_mode=args.test)
        ableton_push.start()
        if args.shell:
            banner = ['Ableton Push Shell',
                      'You may leave this shell by typing `exit`, `q` or pressing Ctrl+D',
                      'ableton_push is the main object.']
            Pysh(dict_to_include={'ableton_push': ableton_push},
                 prompt="AbletonPush$ ",
                 banner=banner)
        else:
            run = True
            while run:
                try:
                    sleep(0.1)
                except KeyboardInterrupt:
                    run = False
                    print("KeyboardInterrupt, exit...")
        ableton_push.quit = True
