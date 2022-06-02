import threading
from time import sleep
import paho.mqtt.client as mqtt
from pythonosc.udp_client import SimpleUDPClient


from Faderport.structure import FaderportControls
from Faderport.structure import Button as FaderportButton
from Faderport.structure import PitchWheel as FaderportPitchWheel

from AbletonPush.structure import PushControls
from AbletonPush.structure import Button as PushButton
from AbletonPush.structure import TouchBar as PushTouchBar
from AbletonPush.structure import Display as PushDisplay


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
        while True:
            if self.quit:
                self.mqtt_client.loop_stop()
                return
            sleep(0.001)

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
        topic = f"{self.controls_push.mqtt_prefix}/{control_object.name}/set_light_mode"
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
