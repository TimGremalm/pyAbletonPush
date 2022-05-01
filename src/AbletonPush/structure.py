from AbletonPush import try_parse_int
from AbletonPush.constants import *


class Button:
    def __init__(self, name: str, ableton_push,
                 midi_type: MIDIType, midi_id: int,
                 luminance_type: LightTypes,
                 channel: int = 0, pad_number: int = None):
        self.name = name
        self.ableton_push = ableton_push
        self.midi_id = midi_id
        self.channel = channel
        self.midi_type = midi_type
        self.luminance_type = luminance_type
        self.pad_number = pad_number
        self.light = None

    def set_light(self, color):
        if self.light == color:
            # print(f"Color {color} is already set for {self.name}.")
            return
        self.ableton_push.button_set_color(self, color)
        self.light = color

    def __repr__(self):
        out = f"Button(name='{self.name}', " \
              f"ableton_push={self.ableton_push}, " \
              f"midi_type={self.midi_type}, channel={self.channel}, midi_id={self.midi_id}, " \
              f"luminance_type={self.luminance_type}"
        if self.pad_number is not None:
            out += f", pad_number={self.pad_number}"
        out += f")"
        return out


class TouchBar:
    def __init__(self, name: str, ableton_push,
                 midi_touch_note: int):
        self.name = name
        self.ableton_push = ableton_push
        self.midi_touch_note = midi_touch_note
        self.midi_pitch_wheel = "pitchwheel"
        self.channel = 0
        self.midi_type = MIDIType.ControlChange
        self.light_mode = None
        self.light_array = None

    def set_light_mode(self, mode: int):
        """
        :type mode: int touch-bar-mode TouchStripModes,
                    enum TouchStripModes,
                    str int of touch-bar-mode representing enum in TouchStripModes,
                    str touch-bar-mode representing enum in TouchStripModes
        """
        mode_argument = mode
        mode_to_set = None
        if self.light_mode == mode:
            # print(f"Mode {mode} is already set for {self.name}.")
            return
        if type(mode_argument) is int:
            mode_to_set = mode
        elif str(type(mode_argument)) == str(TouchStripModes):
            mode_to_set = mode_argument.value
        elif type(mode_argument) is bytes or type(mode_argument) is str:
            # Convert bytes to str
            if type(mode_argument) is bytes:
                mode_argument = mode_argument.decode()
            # Parse color argument
            if try_parse_int(mode_argument) is not None:
                # It's an integer
                mode_to_set = int(mode_argument)
            elif mode_argument in TouchStripModes.__members__:
                mode_to_set = TouchStripModes[mode_argument].value
            else:
                raise Exception(f"Can't find mode {mode_argument} in enum TouchStripModes.")
        else:
            raise Exception(f"Mode argument {mode_argument} is not valid for set_light_mode().")

        # Validate ranges
        if mode_to_set < 0:
            raise Exception(f"Mode {mode_to_set} for can't be negative.")
        if mode_to_set >= len(TouchStripModes.__members__):
            raise Exception(f"Mode {mode_to_set} can't be more than max of TouchStripModes.")

        # Set mode
        self.ableton_push.touch_strip_set_mode(mode_to_set)
        self.light_mode = mode
        self.light_array = None

    def set_light_array(self, array: list):
        """
        :type array: list of 24 led-levels, bottom to top order. A level can be 0-3,
                     str of 24 comma-separated led-levels
        """
        array_argument = array
        array_to_set = None
        if self.light_array == array:
            # print(f"Array {array} is already set for {self.name}.")
            return
        if type(array_argument) is list:
            array_to_set = array_argument
        elif type(array_argument) is bytes or type(array_argument) is str:
            # Convert bytes to str
            if type(array_argument) is bytes:
                array_argument = array_argument.decode()
            splits = array_argument.split(",")
            array_to_set = []
            for s in splits:
                array_to_set.append(try_parse_int(s))
        else:
            raise Exception(f"Array argument {array_argument} is not valid for set_light_array().")

        # Check that touch bar is set in addressable
        if self.light_mode != TouchStripModes.Addressable:
            print("Manually setting mode to TouchStripModes.Addressable.")
            self.set_light_mode(TouchStripModes.Addressable)

        # Set mode
        self.ableton_push.touch_strip_set_leds(array_to_set)
        self.light_array = array

    def __repr__(self):
        out = f"TouchBar(name='{self.name}', " \
              f"ableton_push={self.ableton_push}, " \
              f"midi_touch_note={self.midi_touch_note}"
        out += f")"
        return out


class Display:
    def __init__(self, name: str, ableton_push):
        self.name = name
        self.ableton_push = ableton_push
        # Init to 68 spaces on all 4 lines
        self.text_lines = {}
        for i in range(1, 5):
            self.text_lines[i] = " "*4*17
        self.brightness = None
        self.contrast = None

    def set_brightness(self, brightness):
        """
        :type brightness: int 0-127
                          str 0-127
        """
        brightness_argument = brightness
        brightness_to_set = None
        if self.brightness == brightness:
            print(f"Brightness {brightness} is already set for {self.name}.")
            return
        if type(brightness_argument) is int:
            brightness_to_set = brightness
        elif type(brightness_argument) is bytes or type(brightness_argument) is str:
            # Convert bytes to str
            if type(brightness_argument) is bytes:
                brightness_argument = brightness_argument.decode()
            # Parse color argument
            if try_parse_int(brightness_argument) is not None:
                # It's an integer
                brightness_to_set = int(brightness_argument)
            else:
                raise Exception(f"Can't parse brightness {brightness_argument}.")
        else:
            raise Exception(f"Brightness argument {brightness_argument} is not valid for set_light_mode().")

        # Validate ranges
        if brightness_to_set < 0:
            raise Exception(f"Brightness {brightness_to_set} for can't be negative.")
        if brightness_to_set > 127:
            raise Exception(f"Brightness {brightness_to_set} can't be more than 127.")

        print(f"Set brightness {brightness_to_set}")
        self.ableton_push.display_set_brightness(brightness_to_set)
        self.brightness = brightness_to_set

    def set_contrast(self, contrast):
        """
        :type contrast: int 0-127
                        str 0-127
        """
        contrast_argument = contrast
        contrast_to_set = None
        if self.contrast == contrast:
            print(f"Contrast {contrast} is already set for {self.name}.")
            return
        if type(contrast_argument) is int:
            contrast_to_set = contrast
        elif type(contrast_argument) is bytes or type(contrast_argument) is str:
            # Convert bytes to str
            if type(contrast_argument) is bytes:
                contrast_argument = contrast_argument.decode()
            # Parse color argument
            if try_parse_int(contrast_argument) is not None:
                # It's an integer
                contrast_to_set = int(contrast_argument)
            else:
                raise Exception(f"Can't parse contrast {contrast_argument}.")
        else:
            raise Exception(f"Contrast argument {contrast_argument} is not valid for set_light_mode().")

        # Validate ranges
        if contrast_to_set < 0:
            raise Exception(f"Contrast {contrast_to_set} for can't be negative.")
        if contrast_to_set > 127:
            raise Exception(f"Contrast {contrast_to_set} can't be more than 127.")

        print(f"Set contrast {contrast_to_set}")
        self.ableton_push.display_set_contrast(contrast_to_set)
        self.contrast = contrast_to_set

    def set_text(self, payload, row: int = None, col: int = None):
        # print(f"set_text {row} {col} {payload}")
        # Validate that we have a row
        colwidth = int(17 / 2)
        if row is None:
            raise Exception("Row must be set.")
        if row < 1 or row > 4:
            raise Exception(f"Row {row} must be between 1-4.")
        if col is None:
            if len(payload) > 17*4:
                raise Exception(f"Text length can only be {17*4} on a full row.")
        else:
            if col < 1 or col > 8:
                raise Exception(f"Col {col} must be between 1-8.")
            if len(payload) > colwidth:
                raise Exception(f"Text length can only be {colwidth} on a full row.")
        if len(payload) < 1:
            raise Exception(f"Text length must be at least 1 character.")

        # Set text
        text_row = self.text_lines[row]
        # print(f"text_row '{text_row}' ({len(text_row)})")
        length = len(payload)
        if col is None:
            text_row = payload + text_row[length:]
        else:
            start = (col-1)*colwidth
            if col % 2 == 0:
                start += 1
            mid_columns = int((col-1)/2)
            start += mid_columns
            diff_column = colwidth - length
            text_row = text_row[:start] + payload + text_row[start+length:]
        if len(text_row) != 17*4:
            raise Exception(f"Length of row {len(text_row)} is not {17*4} characters.")
        # print(f"text_row '{text_row}' ({len(text_row)})")
        if self.text_lines[row] == text_row:
            print("Same as before")
            return
        self.ableton_push.display_set_text(text=text_row, line=row-1)
        self.text_lines[row] = text_row

    def clear_text(self, separator: str = " ", row: int = None, col: int = None):
        # print(f"clear_text {col}")
        blank_row = ""
        if len(separator) == 0:
            separator = " "
        elif len(separator) > 1:
            raise Exception(f"Separator {separator} must be 1 character.")
        if col is None:
            blank_row = separator*17*4
        else:
            blank_row = separator*8
        # self.ableton_push.display_clear_text(line=row, column=col, separator=separator)
        if row is None:
            # Update all 4 rows in column
            for i in range(1,5):
                self.set_text(payload=blank_row, row=i, col=col)
        else:
            self.set_text(payload=blank_row, row=row, col=col)

    def __repr__(self):
        out = f"Display(name='{self.name}', " \
              f"ableton_push={self.ableton_push}"
        out += f")"
        return out


class PushControls:
    def __init__(self, ableton_push):
        self.ableton_push = ableton_push
        self.topics_in = {}
        self.topics_out = {}
        # Left buttons
        self.add_control_button(btn=Button(name="left_tap_tempo", ableton_push=ableton_push,
                                           midi_type=MIDIType.ControlChange,
                                           midi_id=3, luminance_type=LightTypes.Yellow))
        self.add_control_button(btn=Button(name="left_metronome", ableton_push=ableton_push,
                                           midi_type=MIDIType.ControlChange,
                                           midi_id=9, luminance_type=LightTypes.Yellow))
        self.add_control_button(btn=Button(name="left_undo", ableton_push=ableton_push,
                                           midi_type=MIDIType.ControlChange,
                                           midi_id=119, luminance_type=LightTypes.Yellow))
        self.add_control_button(btn=Button(name="left_delete", ableton_push=ableton_push,
                                           midi_type=MIDIType.ControlChange,
                                           midi_id=118, luminance_type=LightTypes.Yellow))
        self.add_control_button(btn=Button(name="left_double", ableton_push=ableton_push,
                                           midi_type=MIDIType.ControlChange,
                                           midi_id=117, luminance_type=LightTypes.Yellow))
        self.add_control_button(btn=Button(name="left_quantize", ableton_push=ableton_push,
                                           midi_type=MIDIType.ControlChange,
                                           midi_id=116, luminance_type=LightTypes.Yellow))
        self.add_control_button(btn=Button(name="left_fixed_length", ableton_push=ableton_push,
                                           midi_type=MIDIType.ControlChange,
                                           midi_id=90, luminance_type=LightTypes.Yellow))
        self.add_control_button(btn=Button(name="left_automation", ableton_push=ableton_push,
                                           midi_type=MIDIType.ControlChange,
                                           midi_id=89, luminance_type=LightTypes.Red))
        self.add_control_button(btn=Button(name="left_duplicate", ableton_push=ableton_push,
                                           midi_type=MIDIType.ControlChange,
                                           midi_id=88, luminance_type=LightTypes.Yellow))
        self.add_control_button(btn=Button(name="left_new", ableton_push=ableton_push, midi_type=MIDIType.ControlChange,
                                           midi_id=87, luminance_type=LightTypes.Yellow))
        self.add_control_button(btn=Button(name="left_record", ableton_push=ableton_push, midi_type=MIDIType.ControlChange,
                                           midi_id=86, luminance_type=LightTypes.Red))
        self.add_control_button(btn=Button(name="left_play", ableton_push=ableton_push, midi_type=MIDIType.ControlChange,
                                           midi_id=85, luminance_type=LightTypes.Green))
        # Grid of pads 8x8
        for pad_number in range(8*8):
            col = (pad_number % 8) + 1  # Get column by modula 8 plus 8
            row = int(pad_number / 8) + 1  # Get row number by dividing by 8 floored
            row_reversed = 8 - row + 1  # Get row number by dividing by 8 floored
            note = 36 + pad_number
            pad_name = f"grid_col{col}_row{row_reversed}"
            self.add_control_button(btn=Button(name=pad_name, ableton_push=ableton_push,
                                               midi_type=MIDIType.Note,
                                               midi_id=note, luminance_type=LightTypes.RGB,
                                               pad_number=pad_number))
        # RGB row above grid
        for i in range(8):
            pad_number = 64 + i
            col = i + 1
            cc = 102 + i
            pad_name = f"grid_col{col}_row0"
            self.add_control_button(btn=Button(name=pad_name, ableton_push=ableton_push,
                                               midi_type=MIDIType.ControlChange,
                                               midi_id=cc, luminance_type=LightTypes.RGB,
                                               pad_number=pad_number))
        # Touch Bar
        self.add_control_touch_bar(touch=TouchBar(name="touch_bar", ableton_push=ableton_push,
                                                  midi_touch_note=12))
        # Display
        self.add_control_display(display=Display(name="display", ableton_push=ableton_push))

    def callback_button_set_light(self, topics, control_object, msg):
        # print(f"callback_button_set for {control_object.name} msg {topics} {msg.payload}")
        try:
            control_object.set_light(msg.payload)
        except Exception as ex:
            self.ableton_push.mqtt_client.publish(topic=f"{topics[0]}/{topics[1]}/error", payload=str(ex))

    def callback_touch_bar_set_light(self, topics, control_object, msg):
        # print(f"callback_touch_bar_set_light for {control_object.name} msg {topics} {msg.payload}")
        try:
            if topics[2] == "set_light_mode":
                control_object.set_light_mode(msg.payload)
            elif topics[2] == "set_light_array":
                control_object.set_light_array(msg.payload)
            else:
                print(f"callback_touch_bar_set_light() Couldn't parse topic {topics[2]}.")
                return
        except Exception as ex:
            self.ableton_push.mqtt_client.publish(topic=f"{topics[0]}/{topics[1]}/error", payload=str(ex))

    def callback_button_event(self, control_object, msg):
        if msg.type == "control_change":
            if msg.value > 0:
                payload = f"{msg.value}"
                topic = f"ableton_push/{control_object.name}/event/down"
            else:
                payload = f"{msg.value}"
                topic = f"ableton_push/{control_object.name}/event/up"
        elif msg.type == "note_on":
            payload = f"{msg.velocity}"
            topic = f"ableton_push/{control_object.name}/event/down"
        elif msg.type == "note_off":
            payload = f"{msg.velocity}"
            topic = f"ableton_push/{control_object.name}/event/up"
        elif msg.type == "polytouch":
            payload = f"{msg.value}"
            topic = f"ableton_push/{control_object.name}/event/aftertouch"
        else:
            return
        self.ableton_push.mqtt_client.publish(topic=topic, payload=payload)

    def callback_touch_bar_event(self, control_object, msg):
        if msg.type == "note_on":
            payload = f"{msg.velocity}"
            if msg.velocity == 0:
                topic = f"ableton_push/{control_object.name}/event/up"
            else:
                topic = f"ableton_push/{control_object.name}/event/down"
        elif msg.type == "note_off":
            payload = f"{msg.velocity}"
            topic = f"ableton_push/{control_object.name}/event/up"
        elif msg.type == "pitchwheel":
            payload = f"{msg.pitch}"
            topic = f"ableton_push/{control_object.name}/event/pitch"
        else:
            return
        self.ableton_push.mqtt_client.publish(topic=topic, payload=payload)

    def callback_display(self, topics, control_object, msg):
        # print(f"callback_display for {control_object.name} msg {topics} {msg.payload}")
        try:
            if topics[2] == "set_brightness":
                control_object.set_brightness(msg.payload)
            elif topics[2] == "set_contrast":
                control_object.set_contrast(msg.payload)
            elif topics[2] == "set_text" or topics[2] == "clear_text":
                # Go through topics, look for row and col
                row = None
                col = None
                payload = msg.payload
                if type(payload) is bytes:
                    payload = payload.decode()
                for i in range(3, len(topics)):
                    if topics[i].startswith("row"):
                        row = try_parse_int(topics[i][3:])
                        if row is None:
                            raise Exception(f"Couldn't parse {topics[i]} as row.")
                    if topics[i].startswith("col"):
                        col = try_parse_int(topics[i][3:])
                        if col is None:
                            raise Exception(f"Couldn't parse {topics[i]} as col.")
                if topics[2] == "set_text":
                    control_object.set_text(payload=payload, row=row, col=col)
                else:
                    control_object.clear_text(col=col, row=row, separator=payload)
            else:
                print(f"callback_display() Couldn't parse topic {topics[2]}.")
                return
        except Exception as ex:
            self.ableton_push.mqtt_client.publish(topic=f"{topics[0]}/{topics[1]}/error", payload=str(ex))

    def add_control_button(self, btn: Button):
        if btn.luminance_type == LightTypes.RGB and btn.pad_number is None:
            raise Exception("Pad number must be set for luminance_type RGB.")
        if btn.name in self.topics_in:
            raise Exception(f"Control {btn.name} already exist in topics_in.")
        self.topics_in[btn.name] = {}
        self.topics_in[btn.name]["set_light"] = (btn, self.callback_button_set_light)

        # Set topics_out[channel][midi_id][type] = (button_object, button_callback)
        if btn.channel not in self.topics_out:
            self.topics_out[btn.channel] = {}
        if btn.midi_id not in self.topics_out[btn.channel]:
            self.topics_out[btn.channel][btn.midi_id] = {}
        if btn.midi_type == MIDIType.ControlChange:
            self.topics_out[btn.channel][btn.midi_id]['control_change'] = (btn, self.callback_button_event)
        elif btn.midi_type == MIDIType.Note:
            self.topics_out[btn.channel][btn.midi_id]['note_on'] = (btn, self.callback_button_event)
            self.topics_out[btn.channel][btn.midi_id]['note_off'] = (btn, self.callback_button_event)
            self.topics_out[btn.channel][btn.midi_id]['polytouch'] = (btn, self.callback_button_event)

        # Set object
        setattr(self, btn.name, btn)

    def add_control_touch_bar(self, touch: TouchBar):
        self.topics_in[touch.name] = {}
        self.topics_in[touch.name]["set_light_mode"] = (touch, self.callback_touch_bar_set_light)
        self.topics_in[touch.name]["set_light_array"] = (touch, self.callback_touch_bar_set_light)

        # Set topics_out[channel][midi_id][type] = (button_object, button_callback)
        if touch.channel not in self.topics_out:
            self.topics_out[touch.channel] = {}
        if touch.midi_touch_note not in self.topics_out[touch.channel]:
            self.topics_out[touch.channel][touch.midi_touch_note] = {}
        if touch.midi_pitch_wheel not in self.topics_out[touch.channel]:
            self.topics_out[touch.channel][touch.midi_pitch_wheel] = {}

        self.topics_out[touch.channel][touch.midi_touch_note]['note_on'] = (touch, self.callback_touch_bar_event)
        self.topics_out[touch.channel][touch.midi_touch_note]['note_off'] = (touch, self.callback_touch_bar_event)
        self.topics_out[touch.channel][touch.midi_pitch_wheel]['pitchwheel'] = (touch, self.callback_touch_bar_event)

        # Set object
        setattr(self, touch.name, touch)

    def add_control_display(self, display: Display):
        self.topics_in[display.name] = {}
        self.topics_in[display.name]["set_brightness"] = (display, self.callback_display)
        self.topics_in[display.name]["set_contrast"] = (display, self.callback_display)
        self.topics_in[display.name][f"set_text"] = (display, self.callback_display)
        self.topics_in[display.name][f"clear_text"] = (display, self.callback_display)
        # Set object
        setattr(self, display.name, display)


if __name__ == '__main__':
    a = Button(name="button_a", midi_type=MIDIType.Note, channel=0, midi_id=46, luminance_type=LightTypes.RedYellow)
    # print(str(a))
    print(repr(a))
    # print(a.is_dirty())
