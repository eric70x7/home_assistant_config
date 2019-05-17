#
# precool the house
#

# debug mode is default
debug = int(data.get('debug', 1))

precool_temp = int(float(hass.states.get('input_number.precool_temp').state)) # 70

# logger.info("Setting precool to {}.".format(precool_temp))

hass.services.call('python_script','set_temp',{'location':'downstairs',
                                               'setpoint':precool_temp,
                                               'debug':debug})

hass.services.call('python_script','set_temp',{'location':'upstairs',
                                               'setpoint':precool_temp,
                                               'debug':debug})
