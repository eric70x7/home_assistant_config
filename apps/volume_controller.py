import appdaemon.plugins.hass.hassapi as hass
import datetime

class VolumeController(hass.Hass):
    def initialize(self):
        # Configurable via apps.yaml
        self.knob = self.args.get('knob', 'input_number.family_room_tv_volume_knob')
        self.tv_media_player = self.args.get('tv_media_player', 'media_player.family_room_tv')
        self.up_trigger = self.args.get('up_trigger', 'input_boolean.family_room_tv_volume_up')
        self.down_trigger = self.args.get('down_trigger', 'input_boolean.family_room_tv_volume_down')
        self.volume_limit = self.args.get('volume_limit', 0.75)
        self.debounce_sec = 0.8

        self.source_map = self.args.get('source_map', {
            'media_player.xantech_dax88_front':  'Family Room TV',
            'media_player.xantech_dax88_center': 'Family Room TV',
            'media_player.xantech_dax88_rear':   'Family Room TV'
        })

        # Cache step size
        self.step = float(self.get_state(self.knob, attribute='step') or 0.01)
        self.last_set_time = None
        
        # Control log output
        self.debug = True

        # Listeners
        self.listen_state(self.handle_tv_power_state, self.tv_media_player, attribute='state')
        self.listen_state(self.handle_up, self.up_trigger)
        self.listen_state(self.handle_down, self.down_trigger)
        self.listen_state(self.handle_knob_change, self.knob)
        self.listen_state(self.handle_tv_volume_change, self.tv_media_player, attribute='volume_level')

        self.log(f"VolumeController initialized | Knob: {self.knob} | TV: {self.tv_media_player} | Zones: {len(self.source_map)}")

    def _should_apply_change(self, old, new):
        if old is None or new is None:
            return False
        old_f, new_f = float(old), float(new)
        return round(old_f / self.step) != round(new_f / self.step)

    def _apply_volume_to_channels(self, vol: float):
        now = datetime.datetime.now()
        if self.last_set_time and (now - self.last_set_time).total_seconds() < self.debounce_sec:
            self.log(f"Debouncing volume set to {vol:.3f}")
            return
        self.last_set_time = now

        clamped_vol = max(0.0, min(vol, self.volume_limit))
        self.log(f"Applying volume {clamped_vol:.3f} to {len(self.source_map)} DAX channels")

        for entity in self.source_map.keys():
            if self.entity_exists(entity):
                self.call_service("media_player/volume_set", entity_id=entity, volume_level=clamped_vol)
            else:
                self.log(f"Warning: Channel entity missing - {entity}")

    def log(self, txt):
        if self.debug:
            super().log(txt)

    def _power_dax_zones(self, turn_on: bool):
        service = "media_player/turn_on" if turn_on else "media_player/turn_off"
        for entity in self.source_map.keys():
            if self.entity_exists(entity):
                self.call_service(service, entity_id=entity)
                self.log(f"{service.replace('/', ' ')} called on {entity}")
            else:
                self.log(f"Skipping {entity} - not found")

    def _set_dax_sources(self):
        self.log("Setting DAX sources from source_map")
        applied = 0
        for entity, src in self.source_map.items():
            if self.entity_exists(entity):
                self.call_service("media_player/select_source", entity_id=entity, source=src)
                self.log(f"Set source to '{src}' on {entity}")
                applied += 1
            else:
                self.log(f"Skipping source set on {entity} - missing")
        if applied == 0:
            self.log("Warning: No sources applied - check source_map entity names")

    def handle_tv_power_state(self, entity, attribute, old, new, kwargs):
        if new == 'on' and old != 'on':
            self.log("TV turned ON - powering on DAX zones and applying source map")
            self._power_dax_zones(True)
            self.run_in(self._delayed_set_sources, 2)  # small delay for reliability

        elif new == 'off' and old != 'off':
            self.log("TV turned OFF - powering off DAX zones")
            self._power_dax_zones(False)

    def _delayed_set_sources(self, kwargs):
        self._set_dax_sources()

    def handle_up(self, entity, attribute, old, new, kwargs):
        if new == "on":
            self.turn_off(entity)
            current = self.get_state(self.knob)
            if current is not None:
                self.call_service("input_number/set_value", entity_id=self.knob,
                                  value=min(float(current) + self.step, 1.0))

    def handle_down(self, entity, attribute, old, new, kwargs):
        if new == "on":
            self.turn_off(entity)
            current = self.get_state(self.knob)
            if current is not None:
                self.call_service("input_number/set_value", entity_id=self.knob,
                                  value=max(float(current) - self.step, 0.0))

    def handle_knob_change(self, entity, attribute, old, new, kwargs):
        if self._should_apply_change(old, new):
            self._apply_volume_to_channels(float(new))

    def handle_tv_volume_change(self, entity, attribute, old, new, kwargs):
        if new is None:
            return
        new_val = float(new)
        current_knob = self.get_state(self.knob)
        if current_knob is None or abs(float(current_knob) - new_val) > 0.005:
            self.log(f"TV remote changed volume to {new_val:.3f}: updating knob")
            self.call_service("input_number/set_value", entity_id=self.knob, value=new_val)

    def entity_exists(self, entity_id):
        return self.get_state(entity_id) is not None