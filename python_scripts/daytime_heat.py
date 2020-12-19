#
# set the daytime heat temp
#

# debug mode is default
debug = int(data.get('debug', 1))

temp = int(float(hass.states.get('input_number.daytime_heat').state)) # 70

# logger.info("Setting precool to {}.".format(precool_temp))

hass.services.call('python_script','set_temp',{'location':'downstairs',
                                               'setpoint':temp,
                                               'set_heat':1,
                                               'debug':debug})

hass.services.call('python_script','set_temp',{'location':'upstairs',
                                               'setpoint':temp,
                                               'set_heat':1,
                                               'debug':debug})
