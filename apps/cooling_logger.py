# File: cooling_logger.py
import appdaemon.plugins.hass.hassapi as hass
import datetime
import json
import os
from sklearn.linear_model import LinearRegression
import numpy as np

class CoolingLogger(hass.Hass):
    def initialize(self):
        self.upstairs_entity = "climate.upstairs_trane_thermostat"
        self.downstairs_entity = "climate.downstairs_trane_thermostat"
        self.outdoor_entity = "sensor.ambient_temp"
        self.log_file = "/config/appdaemon/cooling_model_log.json"
        self.model_entity_up = "sensor.cooling_model_upstairs"
        self.model_entity_down = "sensor.cooling_model_downstairs"
        
        # Track state for each unit
        self.last_state_up = "off"
        self.last_time_up = None
        self.last_temp_up = None
        self.last_state_down = "off"
        self.last_time_down = None
        self.last_temp_down = None
        
        # Load logs
        logs = self.load_log()
        self.cooling_log_up = logs.get("upstairs", [])
        self.cooling_log_down = logs.get("downstairs", [])
        
        self.listen_state(self.track_cooling_up, self.upstairs_entity)
        self.listen_state(self.track_cooling_down, self.downstairs_entity)

    def load_log(self):
        try:
            with open(self.log_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"upstairs": [], "downstairs": []}

    def save_log(self):
        logs = {"upstairs": self.cooling_log_up, "downstairs": self.cooling_log_down}
        with open(self.log_file, "w") as f:
            json.dump(logs, f)

    def get_temperatures(self):
        upstairs_temp = float(self.get_state(self.upstairs_entity, attribute="current_temperature") or 68.0)
        downstairs_temp = float(self.get_state(self.downstairs_entity, attribute="current_temperature") or 68.0)
        outdoor_temp = float(self.get_state(self.outdoor_entity) or 77.0)
        return upstairs_temp, downstairs_temp, outdoor_temp

    def track_cooling_up(self, entity, attribute, old, new, kwargs):
        now = datetime.datetime.now()
        upstairs_temp, _, outdoor_temp = self.get_temperatures()
        
        if self.last_time_up and self.last_temp_up:
            runtime = (now - self.last_time_up).seconds / 60
            if old == "cool" and new == "off" and runtime > 0:
                temp_drop = self.last_temp_up - upstairs_temp
                if temp_drop > 0:
                    minutes_per_degree = runtime / temp_drop
                    self.cooling_log_up.append([outdoor_temp, self.last_temp_up, minutes_per_degree])
                    self.save_log()
                    self.log(f"Upstairs: Outdoor={outdoor_temp}°F, Start={self.last_temp_up}°F, "
                             f"Minutes/°F={minutes_per_degree:.1f}")
                    self.train_model("upstairs")

        self.last_state_up = new
        self.last_time_up = now
        self.last_temp_up = upstairs_temp

    def track_cooling_down(self, entity, attribute, old, new, kwargs):
        now = datetime.datetime.now()
        _, downstairs_temp, outdoor_temp = self.get_temperatures()
        
        if self.last_time_down and self.last_temp_down:
            runtime = (now - self.last_time_down).seconds / 60
            if old == "cool" and new == "off" and runtime > 0:
                temp_drop = self.last_temp_down - downstairs_temp
                if temp_drop > 0:
                    minutes_per_degree = runtime / temp_drop
                    self.cooling_log_down.append([outdoor_temp, self.last_temp_down, minutes_per_degree])
                    self.save_log()
                    self.log(f"Downstairs: Outdoor={outdoor_temp}°F, Start={self.last_temp_down}°F, "
                             f"Minutes/°F={minutes_per_degree:.1f}")
                    self.train_model("downstairs")

        self.last_state_down = new
        self.last_time_down = now
        self.last_temp_down = downstairs_temp

    def train_model(self, zone):
        log = self.cooling_log_up if zone == "upstairs" else self.cooling_log_down
        entity = self.model_entity_up if zone == "upstairs" else self.model_entity_down
        
        if len(log) < 10:
            return
        
        data = np.array(log)
        X = data[:, :2]  # outdoor_temp, indoor_start
        y = data[:, 2]   # minutes_per_degree
        
        model = LinearRegression()
        model.fit(X, y)
        
        coeffs = {"a": model.coef_[0], "b": model.coef_[1], "c": model.intercept_}
        self.set_state(entity, state="trained",
                      attributes={"a": coeffs["a"], "b": coeffs["b"], "c": coeffs["c"],
                                 "sample_size": len(log)})
        self.log(f"{zone} model: a={coeffs['a']:.3f}, b={coeffs['b']:.3f}, c={coeffs['c']:.3f}")