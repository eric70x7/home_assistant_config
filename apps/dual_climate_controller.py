# File: dual_climate_controller.py
import appdaemon.plugins.hass.hassapi as hass
import datetime

class DualClimateController(hass.Hass):
    def initialize(self):
        self.sense_entity = "sensor.energy_usage"
        self.outdoor_entity = "sensor.ambient_temp"
        self.weather_entity = "weather.pirateweather"
        self.upstairs_entity = "climate.upstairs_trane_thermostat"
        self.downstairs_entity = "climate.downstairs_trane_thermostat"
        # TODO: change these to use input numbers and update wherever they are used
        self.max_demand_entity = "input_number.kwh_limit" # kWh
        self.comfort_min_entity = "input_number.target_temp" # °F
        self.comfort_max_entity = "input_number.hi_temp" # °F
        self.ml_entity_up = "sensor.cooling_model_upstairs"
        self.ml_entity_down = "sensor.cooling_model_downstairs"
        self.run_every(self.control_acs, "now", 300)

    def get_sense_power(self):
        power = self.get_state(self.sense_entity)
        return float(power) if power else 0.0

    def get_temperatures(self):
        upstairs_temp = float(self.get_state(self.upstairs_entity, attribute="current_temperature") or 68.0)
        downstairs_temp = float(self.get_state(self.downstairs_entity, attribute="current_temperature") or 68.0)
        outdoor_temp = float(self.get_state(self.outdoor_entity) or 77.0)
        return upstairs_temp, downstairs_temp, outdoor_temp

    def get_max_demand(self):
        return 1000*float(self.get_state(self.max_demand_entity) or 1.0)

    def get_comfort_setpoints(self):
        comfort_min = float(self.get_state(self.comfort_min_entity) or 72.0)
        comfort_max = float(self.get_state(self.comfort_max_entity) or 78.0)
        return comfort_min, comfort_max
    
    def get_forecast_high(self):
        forecast = self.get_state(self.weather_entity, attribute="forecast")
        if forecast:
            return max(float(f["temperature"]) for f in forecast[:24])
        return 100.0

    def calculate_pre_cool_offset(self, forecast_high):
        return min(2.0 + 0.1 * (forecast_high - 90.0), 6.0)

    def calculate_comfort_max(self, forecast_high):
        comfort_max, _ = self.get_comfort_setpoints()
        return min(comfort_max + 0.05 * (forecast_high - 100.0), 78.0)

    def predict_cooling_time(self, outdoor_temp, upstairs_temp, downstairs_temp):
        """Get ML predictions for both units, return the slower one"""
        up_model = self.get_state(self.ml_entity_up, attribute="all")
        down_model = self.get_state(self.ml_entity_down, attribute="all")
        
        # Default fallback
        default = min(10.0 + 0.1 * (outdoor_temp - 90.0), 20.0)
        
        # Upstairs prediction
        if up_model and "attributes" in up_model:
            attrs = up_model["attributes"]
            up_time = attrs.get("a", 0.1) * outdoor_temp + attrs.get("b", -0.05) * upstairs_temp + attrs.get("c", 5.0)
        else:
            up_time = default
        
        # Downstairs prediction
        if down_model and "attributes" in down_model:
            attrs = down_model["attributes"]
            down_time = attrs.get("a", 0.1) * outdoor_temp + attrs.get("b", -0.05) * downstairs_temp + attrs.get("c", 5.0)
        else:
            down_time = default
        
        return max(up_time, down_time)  # Use slower rate for pre-cool planning

    def set_ac_states(self, state, target_temp):
        self.call_service("climate/set_hvac_mode", entity_id=self.upstairs_entity, hvac_mode=state)
        self.call_service("climate/set_hvac_mode", entity_id=self.downstairs_entity, hvac_mode=state)
        self.call_service("climate/set_temperature", entity_id=self.upstairs_entity, temperature=target_temp)
        self.call_service("climate/set_temperature", entity_id=self.downstairs_entity, temperature=target_temp)

    def control_acs(self, kwargs):
        now = datetime.datetime.now()
        total_power = self.get_sense_power()
        upstairs_temp, downstairs_temp, outdoor_temp = self.get_temperatures()
        avg_temp = (upstairs_temp + downstairs_temp) / 2
        
        peak_start = datetime.time(16, 0)
        peak_end = datetime.time(19, 0)
        
        forecast_high = self.get_forecast_high()
        pre_cool_offset = self.calculate_pre_cool_offset(forecast_high)
        adjusted_comfort_max = self.calculate_comfort_max(forecast_high)
        pre_cool_hours = 3 if forecast_high > 105.0 else 2
        
        pre_cool_start = (datetime.datetime.combine(datetime.date.today(), peak_start) - 
                         datetime.timedelta(hours=pre_cool_hours)).time()

        comfort_min, _ = self.get_comfort_setpoints()

        # ML-driven pre-cool timing
        if pre_cool_start <= now.time() < peak_start:
            target_temp = comfort_min - pre_cool_offset
            cooling_time_per_degree = self.predict_cooling_time(outdoor_temp, upstairs_temp, downstairs_temp)
            temp_to_drop = max(avg_temp - target_temp, 0)
            total_cool_time = cooling_time_per_degree * temp_to_drop
            self.log(f"Predicted: {total_cool_time:.1f} min to drop {temp_to_drop:.1f}°F")

        max_demand = self.get_max_demand()

        # Control logic
        if now.weekday() >= 5:
            self.set_ac_states("cool", comfort_min)
        elif pre_cool_start <= now.time() < peak_start:
            target_temp = comfort_min - pre_cool_offset
            if outdoor_temp > 100.0:
                target_temp -= 1.0
            if avg_temp > target_temp and total_power < max_demand * 1.5:
                self.set_ac_states("cool", target_temp)
            else:
                self.set_ac_states("off", target_temp)
        elif peak_start <= now.time() <= peak_end:
            target_temp = adjusted_comfort_max
            if avg_temp > adjusted_comfort_max and total_power < max_demand:
                self.set_ac_states("cool", target_temp)
            else:
                self.set_ac_states("off", target_temp)
        else:
            target_temp = comfort_min
            if avg_temp > comfort_min and total_power < max_demand * 1.5:
                self.set_ac_states("cool", target_temp)
            else:
                self.set_ac_states("off", target_temp)

        self.log(f"Power: {total_power}W, Outdoor: {outdoor_temp}°F, Forecast High: {forecast_high}°F, "
                 f"ACs: {self.get_state(self.upstairs_entity)}, Avg Temp: {avg_temp}°F")