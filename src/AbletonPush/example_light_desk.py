import threading
from time import sleep, time
from enum import Enum
import paho.mqtt.client as mqtt
from pythonosc.udp_client import SimpleUDPClient
import colorsys

from Faderport.structure import FaderportControls
from Faderport.structure import Button as FaderportButton
from Faderport.structure import PitchWheel as FaderportPitchWheel
from Faderport.constants import LightTypes as FaderportLightTypes

from AbletonPush.structure import PushControls
from AbletonPush.structure import Button as PushButton
from AbletonPush.structure import TouchBar as PushTouchBar
from AbletonPush.structure import Display as PushDisplay
from AbletonPush.helper_functions import try_parse_int, format_float_precision, translate
from AbletonPush.constants import LightTypes as PushLightTypes
from AbletonPush.constants import ColorsRedYellow as PushColorsRedYellow


class ValueHolder:
    def __init__(self, name: str, description: str, button, light_desk, group_row, group_col):
        self.name = name
        self.description = description
        self.button = button
        self.light_desk = light_desk
        self.group_row = group_row
        self.group_col = group_col
        self.selected = False
        # Value
        self._value = 0
        self.value_previous = 0
        self.light_desk.values.append(self)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value_to_set):
        self._value = value_to_set
        if self._value < 0:
            self._value = 0
        if self._value > 65535:
            self._value = 65535

    @property
    def value_float(self):
        return self._value / 65535

    @value_float.setter
    def value_float(self, value_to_set):
        self._value = int(value_to_set * 65535)
        if self._value < 0:
            self._value = 0
        if self._value > 65535:
            self._value = 65535

    def get_text(self):
        shifted_value = self.value >> 8
        out = f"{self.name:4} {shifted_value:03}"
        return out

    def osc_send(self):
        self.light_desk.osc.send_message(f"/{self.group_col.name}/{self.name}", self.value_float)

    def __repr__(self):
        out = f"ValueHolder(name='{self.name}'"
        out += f", description={self.description}"
        out += f", group_row={self.group_row}"
        out += f", group_col={self.group_col}"
        out += f")"
        return out


class ButtonValue(ValueHolder):
    def __init__(self, name: str, description: str, light_hue: float, light_saturation: float,
                 button, light_desk, group_row, group_col):
        super(ButtonValue, self).__init__(name=name, description=description, button=button,
                                          light_desk=light_desk, group_row=group_row, group_col=group_col)
        self.light_saturation = light_saturation
        self.light_hue = light_hue
        self.group_col.buttons[self.name] = self
        if button.luminance_type in list(PushLightTypes):
            self.mqtt_prefix = self.light_desk.controls_push.mqtt_prefix
        elif button.luminance_type in list(FaderportLightTypes):
            self.mqtt_prefix = self.light_desk.controls_faderport.mqtt_prefix
        else:
            self.mqtt_prefix = "unknown"
        setattr(self.group_col, self.name, self)
        self.light_desk.callbacks[(self.mqtt_prefix, self.button.name)] = (self.cb_event, self)

    def cb_event(self, *args, **kwargs):
        # print(f"cb_event {args} {kwargs}.")
        if kwargs['event'] == 'down':
            # print(kwargs['data'])
            self.selected = True
            self.light_desk.selected_group = self.group_row.name
        elif kwargs['event'] == 'up':
            # print(kwargs['data'])
            self.selected = False


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
            ButtonValue(name=btn['name'], description=btn['description'],
                        light_hue=btn['hue'], light_saturation=btn['sat'],
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
        self.callbacks = {}
        self.selected_group = None
        self.selected_group_previous = None
        self.pushed_row_previous = []

    def cb_event_sliders(self, *args, **kwargs):
        # print(f"cb_event {args} {kwargs}.")
        if kwargs['event'] == 'pitch':
            slider = kwargs['data']
            slider_value = try_parse_int(kwargs['payload']) + 8192
            slider_value_float = slider_value / (2**14-1)
            column_i = slider.pitchwheel_channel + 1
            # print(slider_value)
            # Change values in corresponding selected column
            if self.selected_group:
                group = self.groups[self.selected_group]
                col = group.columns[f"{self.selected_group}{column_i}"]
                val = col.buttons['Sli4']
                val.value_float = slider_value_float

    def cb_event_encoders(self, *args, **kwargs):
        if kwargs['event'] == 'rotate':
            # print(kwargs)
            selected_values = self.get_selected_values(filter_col=kwargs['data'].midi_rotate - 70)
            # Update only selected values in the same column as the encoder
            for val in selected_values:
                enc_value = try_parse_int(kwargs['payload']) * 500
                val.value += enc_value
                # print(format_float_precision(val.value_float, 2))

    def cb_event_encoder_all(self, *args, **kwargs):
        if kwargs['event'] == 'rotate':
            # print(kwargs)
            # Update all selected values
            selected_values = self.get_selected_values()
            for val in selected_values:
                enc_value = try_parse_int(kwargs['payload']) * 500
                val.value += enc_value
                # print(format_float_precision(val.value_float, 2))

    def cb_event_beat_tap(self, *args, **kwargs):
        if kwargs['event'] == 'down':
            self.osc.send_message("/beat_tap", 1)
        elif kwargs['event'] == 'up':
            self.osc.send_message("/beat_tap", 0)

    def get_selected_values(self, filter_col: int = None, filter_group: str = None):
        values_selected = []
        for group_key, group in self.groups.items():
            for col_key, col in group.columns.items():
                for btn_key, btn in col.buttons.items():
                    if btn.selected:
                        if filter_col:
                            if col.column_i == filter_col:
                                values_selected.append(btn)
                        elif filter_group:
                            if group_key == filter_group:
                                values_selected.append(btn)
                        else:
                            values_selected.append(btn)
        return values_selected

    def get_pushed_rows(self):
        pushed_rows = []
        for val in self.get_selected_values():
            if val.group_row not in pushed_rows:
                pushed_rows.append(val.group_row)
        return pushed_rows

    def add_controls_and_groups(self):
        GroupRow(name='T', description="Group T", light_desk=self,
                 cols=[[{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.0, 'sat': 1.0,
                         'button': self.controls_push.grid_col1_rowt1},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.1, 'sat': 1.0,
                         'button': self.controls_faderport.col1_select}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.0, 'sat': 1.0,
                         'button': self.controls_push.grid_col2_rowt1},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.1, 'sat': 1.0,
                         'button': self.controls_faderport.col2_select}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.0, 'sat': 1.0,
                         'button': self.controls_push.grid_col3_rowt1},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.1, 'sat': 1.0,
                         'button': self.controls_faderport.col3_select}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.0, 'sat': 1.0,
                         'button': self.controls_push.grid_col4_rowt1},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.1, 'sat': 1.0,
                         'button': self.controls_faderport.col4_select}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.0, 'sat': 1.0,
                         'button': self.controls_push.grid_col5_rowt1},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.1, 'sat': 1.0,
                         'button': self.controls_faderport.col5_select}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.0, 'sat': 1.0,
                         'button': self.controls_push.grid_col6_rowt1},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.1, 'sat': 1.0,
                         'button': self.controls_faderport.col6_select}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.0, 'sat': 1.0,
                         'button': self.controls_push.grid_col7_rowt1},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.1, 'sat': 1.0,
                         'button': self.controls_faderport.col7_select}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.0, 'sat': 1.0,
                         'button': self.controls_push.grid_col8_rowt1},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.1, 'sat': 1.0,
                         'button': self.controls_faderport.col8_select}],
                       ]
                 )
        GroupRow(name='A', description="Group A  ", light_desk=self,
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
        GroupRow(name='B', description="Floor   ", light_desk=self,
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
        GroupRow(name='C', description="Skog    ", light_desk=self,
                 cols=[[{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.6, 'sat': 0.0,
                         'button': self.controls_push.grid_col1_row6},
                        {'name': 'Val2', 'description': 'Do something Val2', 'hue': 0.7, 'sat': 1.0,
                         'button': self.controls_push.grid_col1_row7},
                        {'name': 'RnR2', 'description': 'Do something Val3', 'hue': 0.8, 'sat': 1.0,
                         'button': self.controls_push.grid_col1_row8}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.6, 'sat': 0.0,
                         'button': self.controls_push.grid_col2_row6},
                        {'name': 'RndA', 'description': 'Do something Val2', 'hue': 0.7, 'sat': 1.0,
                         'button': self.controls_push.grid_col2_row7},
                        {'name': 'RnR1', 'description': 'Do something Val3', 'hue': 0.8, 'sat': 1.0,
                         'button': self.controls_push.grid_col2_row8}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.0, 'sat': 0.0,
                         'button': self.controls_push.grid_col3_row6},
                        {'name': 'RndB', 'description': 'Do something Val2', 'hue': 0.7, 'sat': 1.0,
                         'button': self.controls_push.grid_col3_row7},
                        {'name': 'RnB2', 'description': 'Do something Val3', 'hue': 0.8, 'sat': 1.0,
                         'button': self.controls_push.grid_col3_row8}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.6, 'sat': 0.0,
                         'button': self.controls_push.grid_col4_row6},
                        {'name': 'Red ', 'description': 'Do something Val2', 'hue': 0.7, 'sat': 1.0,
                         'button': self.controls_push.grid_col4_row7},
                        {'name': 'RnB1', 'description': 'Do something Val3', 'hue': 0.8, 'sat': 1.0,
                         'button': self.controls_push.grid_col4_row8}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.6, 'sat': 0.0,
                         'button': self.controls_push.grid_col5_row6},
                        {'name': 'Grn ', 'description': 'Do something Val2', 'hue': 0.7, 'sat': 1.0,
                         'button': self.controls_push.grid_col5_row7},
                        {'name': 'HlB2', 'description': 'Do something Val3', 'hue': 0.8, 'sat': 1.0,
                         'button': self.controls_push.grid_col5_row8}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.6, 'sat': 0.0,
                         'button': self.controls_push.grid_col6_row6},
                        {'name': 'Blu ', 'description': 'Do something Val2', 'hue': 0.7, 'sat': 1.0,
                         'button': self.controls_push.grid_col6_row7},
                        {'name': 'HlB1', 'description': 'Do something Val3', 'hue': 0.8, 'sat': 1.0,
                         'button': self.controls_push.grid_col6_row8}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.6, 'sat': 0.0,
                         'button': self.controls_push.grid_col7_row6},
                        {'name': 'Rain', 'description': 'Do something Val2', 'hue': 0.7, 'sat': 1.0,
                         'button': self.controls_push.grid_col7_row7},
                        {'name': 'OdB2', 'description': 'Do something Val3', 'hue': 0.8, 'sat': 1.0,
                         'button': self.controls_push.grid_col7_row8}],
                       [{'name': 'Val1', 'description': 'Do something Val1', 'hue': 0.6, 'sat': 0.0,
                         'button': self.controls_push.grid_col8_row6},
                        {'name': 'Abst', 'description': 'Do something Val2', 'hue': 0.7, 'sat': 1.0,
                         'button': self.controls_push.grid_col8_row7},
                        {'name': 'OdB1', 'description': 'Do something Val3', 'hue': 0.8, 'sat': 1.0,
                         'button': self.controls_push.grid_col8_row8}],
                       ]
                 )
        # Add 8 sliders
        self.callbacks[(self.controls_faderport.mqtt_prefix, "col1_slider")] = (self.cb_event_sliders, self.controls_faderport.col1_slider)
        self.callbacks[(self.controls_faderport.mqtt_prefix, "col2_slider")] = (self.cb_event_sliders, self.controls_faderport.col2_slider)
        self.callbacks[(self.controls_faderport.mqtt_prefix, "col3_slider")] = (self.cb_event_sliders, self.controls_faderport.col3_slider)
        self.callbacks[(self.controls_faderport.mqtt_prefix, "col4_slider")] = (self.cb_event_sliders, self.controls_faderport.col4_slider)
        self.callbacks[(self.controls_faderport.mqtt_prefix, "col5_slider")] = (self.cb_event_sliders, self.controls_faderport.col5_slider)
        self.callbacks[(self.controls_faderport.mqtt_prefix, "col6_slider")] = (self.cb_event_sliders, self.controls_faderport.col6_slider)
        self.callbacks[(self.controls_faderport.mqtt_prefix, "col7_slider")] = (self.cb_event_sliders, self.controls_faderport.col7_slider)
        self.callbacks[(self.controls_faderport.mqtt_prefix, "col8_slider")] = (self.cb_event_sliders, self.controls_faderport.col8_slider)
        # Add 8 encoders
        self.callbacks[(self.controls_push.mqtt_prefix, "grid_col1_knob")] = (self.cb_event_encoders, self.controls_push.grid_col1_knob)
        self.callbacks[(self.controls_push.mqtt_prefix, "grid_col2_knob")] = (self.cb_event_encoders, self.controls_push.grid_col2_knob)
        self.callbacks[(self.controls_push.mqtt_prefix, "grid_col3_knob")] = (self.cb_event_encoders, self.controls_push.grid_col3_knob)
        self.callbacks[(self.controls_push.mqtt_prefix, "grid_col4_knob")] = (self.cb_event_encoders, self.controls_push.grid_col4_knob)
        self.callbacks[(self.controls_push.mqtt_prefix, "grid_col5_knob")] = (self.cb_event_encoders, self.controls_push.grid_col5_knob)
        self.callbacks[(self.controls_push.mqtt_prefix, "grid_col6_knob")] = (self.cb_event_encoders, self.controls_push.grid_col6_knob)
        self.callbacks[(self.controls_push.mqtt_prefix, "grid_col7_knob")] = (self.cb_event_encoders, self.controls_push.grid_col7_knob)
        self.callbacks[(self.controls_push.mqtt_prefix, "grid_col8_knob")] = (self.cb_event_encoders, self.controls_push.grid_col8_knob)
        # Add the right encode to control all
        self.callbacks[(self.controls_push.mqtt_prefix, "right_knob")] = (self.cb_event_encoder_all, self.controls_push.right_knob)
        # Beat tap
        self.callbacks[(self.controls_push.mqtt_prefix, "left_tap_tempo")] = (self.cb_event_beat_tap, self.controls_push.left_tap_tempo)

        # Add slider values for all groups
        for group_key, group in self.groups.items():
            for col_key, col in group.columns.items():
                slider_name = 'Sli4'
                if col.column_i == 1:
                    col.buttons[slider_name] = ValueHolder(name=slider_name, description="Faderport Slider",
                                                           button=self.controls_faderport.col1_slider,
                                                           light_desk=self, group_row=group, group_col=col)
                elif col.column_i == 2:
                    col.buttons[slider_name] = ValueHolder(name=slider_name, description="Faderport Slider",
                                                           button=self.controls_faderport.col2_slider,
                                                           light_desk=self, group_row=group, group_col=col)
                elif col.column_i == 3:
                    col.buttons[slider_name] = ValueHolder(name=slider_name, description="Faderport Slider",
                                                           button=self.controls_faderport.col3_slider,
                                                           light_desk=self, group_row=group, group_col=col)
                elif col.column_i == 4:
                    col.buttons[slider_name] = ValueHolder(name=slider_name, description="Faderport Slider",
                                                           button=self.controls_faderport.col4_slider,
                                                           light_desk=self, group_row=group, group_col=col)
                elif col.column_i == 5:
                    col.buttons[slider_name] = ValueHolder(name=slider_name, description="Faderport Slider",
                                                           button=self.controls_faderport.col5_slider,
                                                           light_desk=self, group_row=group, group_col=col)
                elif col.column_i == 6:
                    col.buttons[slider_name] = ValueHolder(name=slider_name, description="Faderport Slider",
                                                           button=self.controls_faderport.col6_slider,
                                                           light_desk=self, group_row=group, group_col=col)
                elif col.column_i == 7:
                    col.buttons[slider_name] = ValueHolder(name=slider_name, description="Faderport Slider",
                                                           button=self.controls_faderport.col7_slider,
                                                           light_desk=self, group_row=group, group_col=col)
                elif col.column_i == 8:
                    col.buttons[slider_name] = ValueHolder(name=slider_name, description="Faderport Slider",
                                                           button=self.controls_faderport.col8_slider,
                                                           light_desk=self, group_row=group, group_col=col)
                setattr(col, slider_name, col.buttons[slider_name])

        # Init Display and colors
        self.controls_push.display.clear_text()
        self.controls_push.display.set_text("Light Table OSC", row=1)
        self.controls_push.display.set_text("Select a group to get started.", row=2)
        self.controls_push.display.set_text("    https://github.com/TimGremalm/pyAbletonPush", row=3)
        self.controls_push.display.set_text("    https://github.com/TimGremalm/pyFaderport", row=4)
        self.controls_faderport.col1_select.set_light(2)
        self.controls_faderport.col2_select.set_light(2)
        self.controls_faderport.col3_select.set_light(2)
        self.controls_faderport.col4_select.set_light(2)
        self.controls_faderport.col5_select.set_light(2)
        self.controls_faderport.col6_select.set_light(2)
        self.controls_faderport.col7_select.set_light(2)
        self.controls_faderport.col8_select.set_light(2)

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
        self.add_controls_and_groups()
        while True:
            if self.quit:
                self.mqtt_client.loop_stop()
                return
            self.draw()
            # Cap to 50 FPS
            sleep(0.020)

    def draw(self):
        # Take care of updated values
        for val in self.values:
            if val.value != val.value_previous:
                self.draw_button(val=val)

        # Check if selected group is changed
        if self.selected_group != self.selected_group_previous:
            # Set sliders
            group = self.groups[self.selected_group]
            for col_key, col in group.columns.items():
                slider = col.buttons['Sli4']
                # Convert to 14-bit value from 16
                downshifted = (slider.value >> 2) - ((2**13)-0)
                slider.button.set_pitch(downshifted)
            # Scroll touch strip to selected position
            if self.selected_group == 'A':
                self.controls_push.touch_bar.set_light_array(9*[0] + 9*[0] + 6*[3])
            elif self.selected_group == 'B':
                self.controls_push.touch_bar.set_light_array(9*[0] + 9*[3] + 6*[0])
            elif self.selected_group == 'C':
                self.controls_push.touch_bar.set_light_array(9*[3] + 9*[0] + 6*[0])
            else:
                self.controls_push.touch_bar.set_light_array(24*[0])
            # Clear display if selecting group for first time
            if self.selected_group_previous is None:
                self.controls_push.display.clear_text()
            # Set previous value to detect change
            self.selected_group_previous = self.selected_group

        # If pushed rows changed, redraw buttons on that row
        if self.get_pushed_rows() != self.pushed_row_previous:
            # Redraw all values in row
            # print(f"Redraw pushed rows {self.get_pushed_rows()}")
            for group_key, group in self.groups.items():
                for col_key, col in group.columns.items():
                    for btn_key, btn in col.buttons.items():
                        self.draw_button(btn)
            self.pushed_row_previous = self.get_pushed_rows()

        # Update display
        if self.selected_group:
            group = self.groups[self.selected_group]
            self.controls_push.display.set_text(f"{group.name} {group.description}", row=1)
            for col_key, col in group.columns.items():
                max_buttons = len(col.buttons)
                if max_buttons > 3:
                    max_buttons = 3
                keys = list(col.buttons.keys())
                for i in range(0, max_buttons):
                    val = col.buttons[keys[i]]
                    self.controls_push.display.set_text(f"{val.get_text()}", row=i+2, col=col.column_i)

    def draw_button(self, val):
        # If row is selected, show all colors in at least a minimum to highlight
        # Check if RGB-mode is available
        if type(val) is ButtonValue:
            # Update color and stuff
            val.osc_send()
            if val.button.luminance_type is PushLightTypes.RGB or val.button.luminance_type is FaderportLightTypes.RGB:
                lightness_min = 0.06
                lightness_max = 0.60
                lightness = translate(value=val.value_float,
                                      left_min=0.0, left_max=1.0,
                                      right_min=lightness_min, right_max=lightness_max)
                if val.group_row not in self.get_pushed_rows():
                    # Make black if row is not pushed down
                    if val.value == 0:
                        lightness = 0
                # Cut lightness in half to not make white
                r, g, b = colorsys.hls_to_rgb(h=val.light_hue, s=val.light_saturation, l=lightness)
                val.button.set_light(f"{int(r * 255)},{int(g * 255)},{int(b * 255)}")
            elif val.button.luminance_type is PushLightTypes.RedYellow:
                lightness_min = 0.15
                lightness_max = 1.00
                lightness = translate(value=val.value_float,
                                      left_min=0.0, left_max=1.0,
                                      right_min=lightness_min, right_max=lightness_max)
                if val.group_row not in self.get_pushed_rows():
                    if val.value == 0:
                        lightness = 0
                nice_colors = [PushColorsRedYellow.Black.value,
                               PushColorsRedYellow.RedDim.value,
                               PushColorsRedYellow.YellowDim.value,
                               PushColorsRedYellow.LimeDim.value,
                               PushColorsRedYellow.GreenDim.value,
                               PushColorsRedYellow.GreenLit.value,
                               PushColorsRedYellow.LimeLit.value,
                               PushColorsRedYellow.YellowLit.value,
                               PushColorsRedYellow.RedLit.value]
                color = int(lightness * (len(nice_colors) - 1))
                val.button.set_light(f"{nice_colors[color]}")
            # print(f"{val.name} updated to {val.value_float}")
        if type(val) is ValueHolder:
            val.osc_send()
        # Set previous value to detect change
        val.value_previous = val.value

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
        if (unit, control) in self.callbacks:
            o = self.callbacks[(unit, control)]
            callback = o[0]
            data = o[1]
            callback(unit=unit, control=control, event=event, data=data, payload=msg.payload)

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
