#
# Manage upstairs and downstairs thermostats
#

class Thermostats:

    def __init__(self):
        self.target_temp = int(float(hass.states.get('input_number.target_temp').state)) # 70
        self.target_hi = int(float(hass.states.get('input_number.hi_temp').state)) # 80
        self.ds = hass.states.get('climate.trane_corporation_model_tzemt524aa21ma_cooling_1')
        self.us = hass.states.get('climate.trane_corporation_model_tzemt524aa21ma_cooling_1_2')
    
    def us_setpoint(self):
        return self.us.attributes['temperature']
    
    def ds_setpoint(self):
        return self.ds.attributes['temperature']

    def limit(self, t):
        if t > self.target_hi:
            logger.info("Limiting setpoint to upper limit of {}".format(self.target_hi))
            return self.target_hi
        elif t < self.target_temp:
            logger.info("Limiting setpoint to target temp of {}".format(self.target_temp))
            return self.target_temp
        return t
        
    def set_us(self, t):
        new_setpoint=self.limit(t)
        logger.info("Setting upstairs to {}".format(new_setpoint))
        us_temp = {'entity_id': climate.trane_corporation_model_tzemt524aa21ma_cooling_1_2, 'temperature': new_setpoint}
        # hass.services.call('climate', 'set_temperature', us_temp)
        
    def set_ds(self, t):
        new_setpoint=self.limit(t)
        logger.info("Setting downstairs to {}".format(new_setpoint))
        ds_temp = {'entity_id': trane_corporation_model_tzemt524aa21ma_cooling_1, 'temperature': new_setpoint}
        # hass.services.call('climate', 'set_temperature', ds_temp)
        
    def adjust(self, delta_t) :
        if delta_t == 0:
            return
        new_us_setpoint=self.us_setpoint()
        new_ds_setpoint=self.ds_setpoint()
        # adjust one thermostat at a time, keeping the upstairs higher
        if delta_t > 0:
            if us_setpoint() > ds_setpoint():
                new_ds_setpoint += delta_t
            else:
                new_us_setpoint += delta_t
        else:
            if (us_setpoint() > ds_setpoint()):
                new_us_setpoint += delta_t
            else:
                new_ds_setpoint += delta_t
        self.set_us(new_us_setpoint)
        self.set_ds(new_ds_setpoint)
        
                
    
