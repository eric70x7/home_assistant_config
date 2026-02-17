import appdaemon.plugins.hass.hassapi as hass
import math

class LogLight(hass.Hass):
    def initialize(self):
        self.run_in(self._setup, 3)

    def _setup(self, kwargs):
        self.log_light = self.get_entity(self.args["log_light_entity"])
        self.real_light = self.get_entity(self.args["real_light_entity"])

        if not (self.log_light.exists() and self.real_light.exists()):
            self.log("Entities not available - setup aborted", level="WARNING")
            return

        self.range = 255
        self.gamma = float(self.args.get("gamma", 3.0))
        self.min_brightness = int(self.args.get("min_brightness", 0))
        self.debug = self.args.get("debug", False)

        # Listeners
        self.log_light.listen_state(self.on_log_brightness_change, attribute="brightness")
        self.real_light.listen_state(self.on_real_brightness_change, attribute="brightness")
        self.log_light.listen_state(self.on_log_state_change, attribute="state")
        self.real_light.listen_state(self.on_real_state_change, attribute="state")

        # Initial sync
        self._sync_initial()

    def _sync_initial(self):
        real_state = self.real_light.get_state()
        if real_state == "on":
            self.log_light.call_service("turn_on")
            real_bri = self.real_light.get_state(attribute="brightness")
            if real_bri is not None and real_bri > 0:
                perceptual = int(self.range * math.pow(real_bri / self.range, 1 / self.gamma))
                perceptual = max(1, min(self.range, perceptual))
                self.log_light.call_service("turn_on", brightness=perceptual)
            else:
                self.log_light.call_service("turn_on", brightness=0)
        else:
            self.log_light.call_service("turn_off")

    def logit(self, entity, attribute, old, new):
        if self.debug:
            self.log(f"{entity}[{attribute}]: {old} → {new}")

    def on_real_state_change(self, entity, attribute, old, new, kwargs):
        self.logit(entity, attribute, old, new)
        current = self.real_light.get_state()
        if new != current:
            service = "light/turn_off" if new == "off" else "light/turn_on"
            self.real_light.call_service(service)

    def on_log_state_change(self, entity, attribute, old, new, kwargs):
        self.logit(entity, attribute, old, new)
        current = self.log_light.get_state()
        if new != current:
            service = "light/turn_off" if new == "off" else "light/turn_on"
            self.log_light.call_service(service)

    def on_log_brightness_change(self, entity, attribute, old, new, kwargs):
        self.logit(entity, attribute, old, new)
        if new is None or new <= 0:
            self.real_light.call_service("turn_off")
            return

        normalized = new / self.range
        physical = self.range * math.pow(normalized, self.gamma)
        physical = max(self.min_brightness, min(self.range, round(physical)))
        self.real_light.call_service("turn_on", brightness=int(physical))

    def on_real_brightness_change(self, entity, attribute, old, new, kwargs):
        self.logit(entity, attribute, old, new)
        if new is None:
            return
        if new <= 0:
            self.log_light.call_service("turn_on", brightness=0)
            return

        normalized = new / self.range
        perceptual = int(self.range * math.pow(normalized, 1 / self.gamma))
        perceptual = max(1, min(self.range, perceptual))
        self.log_light.call_service("turn_on", brightness=perceptual)