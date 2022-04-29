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
        self.light_previous = None

    def set_light(self, color):
        self.ableton_push.button_set_color(self, color)
        # self.light = 0
        # self.light_previous = 0

    def __repr__(self):
        out = f"Button(name='{self.name}', " \
              f"midi_type={self.midi_type}, channel={self.channel}, midi_id={self.midi_id}, " \
              f"luminance_type={self.luminance_type}"
        if self.pad_number is not None:
            out += f", pad_number={self.pad_number}"
        out = f")"
        return out


class PushControls:
    def __init__(self, ableton_push):
        self.ableton_push = ableton_push
        self.topics_in = {}
        self.topics_out = {}
        self.add_control_button(btn=Button(name="play", ableton_push=ableton_push, midi_type=MIDIType.ControlChange,
                                           midi_id=85, luminance_type=LightTypes.Green))
        self.add_control_button(btn=Button(name="record", ableton_push=ableton_push, midi_type=MIDIType.ControlChange,
                                           midi_id=86, luminance_type=LightTypes.Red))
        self.add_control_button(btn=Button(name="grid_col_a_row_1", ableton_push=ableton_push,
                                           midi_type=MIDIType.Note,
                                           midi_id=36, luminance_type=LightTypes.RGB,
                                           pad_number=0))

    def callback_button_set_light(self, topics, control_object, msg):
        # print(f"callback_button_set for {control_object.name} msg {topics} {msg.payload}")
        try:
            control_object.set_light(msg.payload)
        except Exception as ex:
            self.ableton_push.mqtt_client.publish(topic=f"{topics[0]}/{topics[1]}/error", payload=str(ex))

    def add_control_button(self, btn: Button):
        if btn.luminance_type == LightTypes.RGB and btn.pad_number is None:
            raise Exception("Pad number must be set for luminance_type RGB.")
        # Set topics_in[btn.name]["set_light"] = (button_object, button_callback)
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
            self.topics_out[btn.channel][btn.midi_id]['control_change'] = 456
        elif btn.midi_type == MIDIType.Note:
            self.topics_out[btn.channel][btn.midi_id]['note'] = 456

        # Set object
        setattr(self, btn.name, btn)


if __name__ == '__main__':
    a = Button(name="button_a", midi_type=MIDIType.Note, channel=0, midi_id=46, luminance_type=LightTypes.RedYellow)
    # print(str(a))
    print(repr(a))
    # print(a.is_dirty())
