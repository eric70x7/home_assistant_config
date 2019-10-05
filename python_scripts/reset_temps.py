#
# reset_temps.py
#

# debug mode is default
debug = int(data.get('debug', 1))

current_ds_setpoint = hass.states.get('climate.trane_corporation_model_tzemt524aa21ma_cooling_1').attributes['temperature']

hass.services.call('python_script','set_temp',{'location':'downstairs',
                                               'setpoint':current_ds_setpoint,
                                               'debug':debug})

current_us_setpoint = hass.states.get('climate.trane_corporation_model_tzemt524aa21ma_cooling_1_2').attributes['temperature']

hass.services.call('python_script','set_temp',{'location':'upstairs',
                                               'setpoint':current_us_setpoint,
                                               'debug':debug})
