#
# reset_temps.py
#

# debug mode is default
debug = int(data.get('debug', 1))

current_ds_setpoint = hass.states.get('climate.downstairs').attributes['temperature']

hass.services.call('python_script','set_temp',{'location':'downstairs',
                                               'setpoint':current_ds_setpoint,
                                               'debug':debug})

current_us_setpoint = hass.states.get('climate.upstairs').attributes['temperature']

hass.services.call('python_script','set_temp',{'location':'upstairs',
                                               'setpoint':current_us_setpoint,
                                               'debug':debug})
