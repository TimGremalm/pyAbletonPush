import threading
from time import sleep
from enum import Enum
import paho.mqtt.client as mqtt
from pythonosc.udp_client import SimpleUDPClient
import colorsys

from Faderport.structure import FaderportControls
from Faderport.structure import Button as FaderportButton
from Faderport.structure import PitchWheel as FaderportPitchWheel

from AbletonPush.structure import PushControls
from AbletonPush.structure import Button as PushButton
from AbletonPush.structure import TouchBar as PushTouchBar
from AbletonPush.structure import Display as PushDisplay


class ButtonState(Enum):
    Init = 0
    Down = 1
    Up = 3


class ZValue:
    def __init__(self, name: str, description: str, light_hue: float, light_saturation: float,
                 button, light_desk, group_row, group_col):
        self.name = name
        self.description = description
        self.light_hue = light_hue
        self.light_saturation = light_saturation
        self.button = button
        self.light_desk = light_desk
        self.group_row = group_row
        self.group_col = group_col
        # Value
        self._value = 0
        self.value_previous = 0
        self.selected = False
        self.group_col.buttons[self.name] = self
        setattr(self.group_col, self.name, self)
        self.light_desk.values.append(self)

    def __repr__(self):
        out = f"ZValue(name='{self.name}'"
        out += f", description={self.description}"
        out += f", group_row={self.group_row}"
        out += f", group_col={self.group_col}"
        out += f")"
        return out

    def osc_send(self):
        pass


class GroupCol:
    def __init__(self, name, column_i: int, light_desk, group_row, buttons):
        self.name = name
        self.column_i = column_i
        self.light_desk = light_desk
        self.group_row = group_row
        self.group_row.columns[self.name] = self
        setattr(self.group_row, self.name, self)
        self.buttons = {}
        for btn_i, btn in enumerate(buttons):
            ZValue(name=btn['name'], description=btn['description'], light_hue=btn['hue'], light_saturation=btn['sat'],
                   button=btn['button'], light_desk=self.light_desk, group_row=self.group_row, group_col=self)

    def __repr__(self):
        out = f"GroupCol(name='{self.name}'"
        out += f")"
        return out


class GroupRow:
    def __init__(self, name: str, description: str, light_desk, cols):
        self.name = name
        self.description = description
        self.light_desk = light_desk
        self.light_desk.groups[self.name] = self
        setattr(self.light_desk, self.name, self)
        self.columns = {}
        for col_i, col in enumerate(cols):
            column_i = col_i + 1
            GroupCol(name=f"{self.name}{column_i}", column_i=column_i,
                     light_desk=self.light_desk, group_row=self, buttons=col)

    def __repr__(self):
        out = f"GroupRow(name='{self.name}'"
        out += f", description={self.description}"
        out += f")"
        return out


class LightDesk(threading.Thread):
    def __init__(self):
        """
        Light Desk Example, MQTT to OSC.
        Connect to Ableton Push and Faderport 8 over MQTT.
        Connect o to an OSC server.
        """
        # Variables
        self.osc_ip = "127.0.0.1"
        self.osc_port = 7700
        self.osc_incoming_port = 9000

        # Instantiate variables
        self.mqtt_client = None
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.quit = False
        self.controls_faderport = None
        self.controls_push = None
        self.osc = None
        self.groups = {}
        self.values = []

    def add_groups(self):
        GroupRow(name='A', description="Group A", light_desk=self,
                 cols=[[{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.0, 'sat': 1.0,
                         'button': self.controls_push.grid_col1_rowt2},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.1, 'sat': 1.0,
                         'button': self.controls_push.grid_col1_row1},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.2, 'sat': 1.0,
                         'button': self.controls_push.grid_col1_row2}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.0, 'sat': 1.0,
                         'button': self.controls_push.grid_col2_rowt2},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.1, 'sat': 1.0,
                         'button': self.controls_push.grid_col2_row1},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.2, 'sat': 1.0,
                         'button': self.controls_push.grid_col2_row2}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.0, 'sat': 1.0,
                         'button': self.controls_push.grid_col3_rowt2},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.1, 'sat': 1.0,
                         'button': self.controls_push.grid_col3_row1},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.2, 'sat': 1.0,
                         'button': self.controls_push.grid_col3_row2}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.0, 'sat': 1.0,
                         'button': self.controls_push.grid_col4_rowt2},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.1, 'sat': 1.0,
                         'button': self.controls_push.grid_col4_row1},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.2, 'sat': 1.0,
                         'button': self.controls_push.grid_col4_row2}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.0, 'sat': 1.0,
                         'button': self.controls_push.grid_col5_rowt2},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.1, 'sat': 1.0,
                         'button': self.controls_push.grid_col5_row1},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.2, 'sat': 1.0,
                         'button': self.controls_push.grid_col5_row2}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.0, 'sat': 1.0,
                         'button': self.controls_push.grid_col6_rowt2},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.1, 'sat': 1.0,
                         'button': self.controls_push.grid_col6_row1},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.2, 'sat': 1.0,
                         'button': self.controls_push.grid_col6_row2}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.0, 'sat': 1.0,
                         'button': self.controls_push.grid_col7_rowt2},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.1, 'sat': 1.0,
                         'button': self.controls_push.grid_col7_row1},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.2, 'sat': 1.0,
                         'button': self.controls_push.grid_col7_row2}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.0, 'sat': 1.0,
                         'button': self.controls_push.grid_col8_rowt2},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.1, 'sat': 1.0,
                         'button': self.controls_push.grid_col8_row1},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.2, 'sat': 1.0,
                         'button': self.controls_push.grid_col8_row2}],
                       ]
                 )
        GroupRow(name='B', description="Group B", light_desk=self,
                 cols=[[{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.3, 'sat': 1.0,
                         'button': self.controls_push.grid_col1_row3},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.4, 'sat': 1.0,
                         'button': self.controls_push.grid_col1_row4},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.5, 'sat': 1.0,
                         'button': self.controls_push.grid_col1_row5}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.3, 'sat': 1.0,
                         'button': self.controls_push.grid_col2_row3},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.4, 'sat': 1.0,
                         'button': self.controls_push.grid_col2_row4},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.5, 'sat': 1.0,
                         'button': self.controls_push.grid_col2_row5}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.3, 'sat': 1.0,
                         'button': self.controls_push.grid_col3_row3},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.4, 'sat': 1.0,
                         'button': self.controls_push.grid_col3_row4},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.5, 'sat': 1.0,
                         'button': self.controls_push.grid_col3_row5}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.3, 'sat': 1.0,
                         'button': self.controls_push.grid_col4_row3},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.4, 'sat': 1.0,
                         'button': self.controls_push.grid_col4_row4},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.5, 'sat': 1.0,
                         'button': self.controls_push.grid_col4_row5}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.3, 'sat': 1.0,
                         'button': self.controls_push.grid_col5_row3},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.4, 'sat': 1.0,
                         'button': self.controls_push.grid_col5_row4},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.5, 'sat': 1.0,
                         'button': self.controls_push.grid_col5_row5}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.3, 'sat': 1.0,
                         'button': self.controls_push.grid_col6_row3},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.4, 'sat': 1.0,
                         'button': self.controls_push.grid_col6_row4},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.5, 'sat': 1.0,
                         'button': self.controls_push.grid_col6_row5}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.3, 'sat': 1.0,
                         'button': self.controls_push.grid_col7_row3},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.4, 'sat': 1.0,
                         'button': self.controls_push.grid_col7_row4},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.5, 'sat': 1.0,
                         'button': self.controls_push.grid_col7_row5}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.3, 'sat': 1.0,
                         'button': self.controls_push.grid_col8_row3},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.4, 'sat': 1.0,
                         'button': self.controls_push.grid_col8_row4},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.5, 'sat': 1.0,
                         'button': self.controls_push.grid_col8_row5}],
                       ]
                 )
        GroupRow(name='C', description="Group C", light_desk=self,
                 cols=[[{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.6, 'sat': 1.0,
                         'button': self.controls_push.grid_col1_row6},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.7, 'sat': 1.0,
                         'button': self.controls_push.grid_col1_row7},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.8, 'sat': 1.0,
                         'button': self.controls_push.grid_col1_row8}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.6, 'sat': 1.0,
                         'button': self.controls_push.grid_col2_row6},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.7, 'sat': 1.0,
                         'button': self.controls_push.grid_col2_row7},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.8, 'sat': 1.0,
                         'button': self.controls_push.grid_col2_row8}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.6, 'sat': 1.0,
                         'button': self.controls_push.grid_col3_row6},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.7, 'sat': 1.0,
                         'button': self.controls_push.grid_col3_row7},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.8, 'sat': 1.0,
                         'button': self.controls_push.grid_col3_row8}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.6, 'sat': 1.0,
                         'button': self.controls_push.grid_col4_row6},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.7, 'sat': 1.0,
                         'button': self.controls_push.grid_col4_row7},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.8, 'sat': 1.0,
                         'button': self.controls_push.grid_col4_row8}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.6, 'sat': 1.0,
                         'button': self.controls_push.grid_col5_row6},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.7, 'sat': 1.0,
                         'button': self.controls_push.grid_col5_row7},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.8, 'sat': 1.0,
                         'button': self.controls_push.grid_col5_row8}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.6, 'sat': 1.0,
                         'button': self.controls_push.grid_col6_row6},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.7, 'sat': 1.0,
                         'button': self.controls_push.grid_col6_row7},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.8, 'sat': 1.0,
                         'button': self.controls_push.grid_col6_row8}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.6, 'sat': 1.0,
                         'button': self.controls_push.grid_col7_row6},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.7, 'sat': 1.0,
                         'button': self.controls_push.grid_col7_row7},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.8, 'sat': 1.0,
                         'button': self.controls_push.grid_col7_row8}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.6, 'sat': 1.0,
                         'button': self.controls_push.grid_col8_row6},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.7, 'sat': 1.0,
                         'button': self.controls_push.grid_col8_row7},
                        {'name': 'Val3', 'description': 'Do something Val3', 'hue': 0.8, 'sat': 1.0,
                         'button': self.controls_push.grid_col8_row8}],
                       ]
                 )
    def run(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self._mqtt_on_connected
        self.mqtt_client.on_message = self._mqtt_on_message
        self.controls_faderport = FaderportControls()
        self.controls_push = PushControls()
        self._setup_faderport()
        self._setup_push()
        self.mqtt_client.connect(host="127.0.0.1")
        self.mqtt_client.loop_start()
        self.osc = SimpleUDPClient(self.osc_ip, self.osc_port)
        self.add_groups()
        while True:
            if self.quit:
                self.mqtt_client.loop_stop()
                return
            # self.draw()
            sleep(0.020)

    def _mqtt_on_connected(self, client, userdata, flags, rc):
        print(f"MQTT Connected with result code {rc}")
        client.subscribe(f"{self.controls_faderport.mqtt_prefix}/#")
        client.subscribe(f"{self.controls_push.mqtt_prefix}/#")

    def _mqtt_on_message(self, client, userdata, msg):
        # print(f"MQTT {msg.topic} {msg.payload}")
        topics = msg.topic.split("/")

        # Ex. topic faderport/col3_mute/event/down
        if len(topics) != 4:
            # Excpect faderport/col3_mute/event/down
            return
        # Parse topics
        unit = topics[0]
        control = topics[1]
        event = topics[3]
        event_concat = f"{topics[2]}/{topics[3]}"
        if unit == self.controls_faderport.mqtt_prefix:
            if control in self.controls_faderport.mqtt_topics_out:
                if event_concat in self.controls_faderport.mqtt_topics_out[control]:
                    control_object = self.controls_faderport.mqtt_topics_out[control][event_concat][0]
                    callback = self.controls_faderport.mqtt_topics_out[control][event_concat][1]
                    # callback(topics, control_object, msg)
                    # print(f"{unit} {control} {event_concat}")
        elif unit == self.controls_push.mqtt_prefix:
            if control in self.controls_push.mqtt_topics_out:
                if event_concat in self.controls_push.mqtt_topics_out[control]:
                    control_object = self.controls_push.mqtt_topics_out[control][event_concat][0]
                    callback = self.controls_push.mqtt_topics_out[control][event_concat][1]
                    # callback(topics, control_object, msg)
                    # print(f"{unit} {control} {event_concat}")

    def _cb_faderport_button_set_light(self, control_object: FaderportButton, value):
        if type(value) is tuple:
            payload = f"{value[0]},{value[1]},{value[2]}"
        else:
            payload = f"{value}"
        topic = f"{self.controls_faderport.mqtt_prefix}/{control_object.name}/set_light"
        self.mqtt_client.publish(topic=topic, payload=payload)

    def _cb_faderport_pitchwheel_set_pitch(self, channel, pitch_value):
        payload = f"{pitch_value}"
        topic = f"{self.controls_faderport.mqtt_prefix}/col{channel+1}_slider/set_pitch"
        self.mqtt_client.publish(topic=topic, payload=payload)

    def _setup_faderport(self):
        for element in self.controls_faderport.elements:
            if type(element) is FaderportButton:
                element.callback_set_light = self._cb_faderport_button_set_light
            elif type(element) is FaderportPitchWheel:
                element.callback_pitchwheel_set_pitch = self._cb_faderport_pitchwheel_set_pitch

    def _cb_push_button_set_light(self, control_object: PushButton, value):
        if type(value) is tuple:
            payload = f"{value[0]},{value[1]},{value[2]}"
        else:
            payload = f"{value}"
        topic = f"{self.controls_push.mqtt_prefix}/{control_object.name}/set_light"
        self.mqtt_client.publish(topic=topic, payload=payload)

    def _cb_push_touch_bar_set_light_mode(self, value):
        payload = f"{value}"
        topic = f"{self.controls_push.mqtt_prefix}/touch_bar/set_light_mode"
        self.mqtt_client.publish(topic=topic, payload=payload)

    def _cb_push_touch_bar_set_light_array(self, array):
        payload = ",".join([str(i) for i in array])
        topic = f"{self.controls_push.mqtt_prefix}/touch_bar/set_light_array"
        self.mqtt_client.publish(topic=topic, payload=payload)

    def _cb_push_display_set_text(self, text, line):
        payload = f"{text}"
        topic = f"{self.controls_push.mqtt_prefix}/display/set_text/row{line+1}"
        self.mqtt_client.publish(topic=topic, payload=payload)

    def _cb_push_display_set_brightness(self, brightness_to_set):
        payload = f"{brightness_to_set}"
        topic = f"{self.controls_push.mqtt_prefix}/display/set_brightness"
        self.mqtt_client.publish(topic=topic, payload=payload)

    def _cb_push_display_set_contrast(self, contrast_to_set):
        payload = f"{contrast_to_set}"
        topic = f"{self.controls_push.mqtt_prefix}/display/set_contrast"
        self.mqtt_client.publish(topic=topic, payload=payload)

    def _setup_push(self):
        for element in self.controls_push.elements:
            if type(element) is PushButton:
                element.callback_set_light = self._cb_push_button_set_light
            elif type(element) is PushTouchBar:
                element.callback_touch_bar_set_light_mode = self._cb_push_touch_bar_set_light_mode
                element.callback_touch_bar_set_light_array = self._cb_push_touch_bar_set_light_array
            elif type(element) is PushDisplay:
                element.callback_display_set_text = self._cb_push_display_set_text
                element.callback_display_set_brightness = self._cb_push_display_set_brightness
                element.callback_display_set_contrast = self._cb_push_display_set_contrast


if __name__ == '__main__':
    title_short = "LightDesk"
    title_long = "Light Desk MQTT to OSC"
    print(title_long)
    lightdesk = LightDesk()
    lightdesk.start()
    from pysh.shell import Pysh  # https://github.com/TimGremalm/pysh

    banner = [f"{title_long} Shell",
              'You may leave this shell by typing `exit`, `q` or pressing Ctrl+D',
              'faderport is the main object.']
    Pysh(dict_to_include={'lightdesk': lightdesk},
         prompt=f"{title_short}$ ",
         banner=banner)
    lightdesk.quit = True