#
# set the temperature to to the target temp
#
    
# debug mode is default
debug = int(data.get('debug', 1))

target_temp = int(float(hass.states.get('input_number.target_temp').state)) # 70

# logger.info("Setting target to {}.".format(target_temp))

hass.services.call('python_script','set_temp',{'location':'downstairs',
                                               'setpoint':target_temp,
                                               'debug':debug})

hass.services.call('python_script','set_temp',{'location':'upstairs',
                                               'setpoint':target_temp,
                                               'debug':debug})
