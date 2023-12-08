import random
import time
import threading
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler
from ovos_bus_client.message import Message

def get_percentage_brightness_from_ha_value(brightness):
    return round(int(brightness) / 255 * 100)

class DiscoSkill(OVOSSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors = ["blue", "yellow", "red", "orange", "green", "white", "purple", "cyan", "magenta", "pink"]
        self.device = "moodlight" # entity name of home assistant device
        self.interval = 1
        self.running = False
        self.disco_thread = None
        self.brightness_increment = 10  # Adjust as needed

    def initialize(self):
        pass

    def start_disco(self):
        feeling = "./skill_disco/feeling.mp3"
        self.speak("Disco lichten aan!")
        self.running = True
        self.play_audio(feeling)
        while self.running:
            self.change_color()
            time.sleep(self.interval)

    def stop(self):
        self.running = False
        if self.disco_thread:
            self.disco_thread.join()  # Wait for the thread to finish
            self.bus.emit(Message("ovos.phal.plugin.homeassistant.device.turn_off", data={"device": self.device}))
        self.speak("Disco lichten uit!")
        self.bus.emit(Message("mycroft.audio.speech.stop"))

    def change_color(self):
        color = random.choice(self.colors)
        self.bus.emit(Message("ovos.phal.plugin.homeassistant.set.light.color", data={"device": self.device, "color": color}))

        # Randomly decide to increase or decrease brightness
        if random.choice([True, False]):
            self.handle_increase_light_brightness()
        else:
            self.handle_decrease_light_brightness()

    def handle_decrease_light_brightness(self):
        brightness = random.randint(5, 20)  # Random decrease value (adjust as needed)
        new_brightness = max(0, self.get_current_brightness() - brightness)
        self.set_brightness(new_brightness)

    def handle_increase_light_brightness(self):
        brightness = random.randint(5, 20)  # Random increase value (adjust as needed)
        new_brightness = min(100, self.get_current_brightness() + brightness)
        self.set_brightness(new_brightness)

    def get_current_brightness(self):
        # Return a simulated or real current brightness value (e.g., between 0 and 100)
        return random.randint(0, 100)

    def set_brightness(self, brightness):
        self.bus.emit(Message("ovos.phal.plugin.homeassistant.device.set_brightness", data={
            "device": self.device,
            "brightness": get_percentage_brightness_from_ha_value(brightness)
        }))

    @intent_handler("disco.intent")
    def handle_disco_intent(self, message):
        if not self.running:
            self.disco_thread = threading.Thread(target=self.start_disco)
            self.disco_thread.start()
        else:
            self.stop()

    @intent_handler("stop.intent")
    def handle_stop_intent(self, message):
        self.stop()

