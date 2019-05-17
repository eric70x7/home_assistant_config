#
# Set a temperature
#

# debug mode is default
debug = int(data.get('debug', 1))
# name can be upstairs or downstairs
location = data.get('location')
setpoint = data.get('setpoint')

good=0
if location == 'upstairs':
    name = 'climate.upstairs'
    saved = 'input_number.upstairs_setpoint'
    good=1
elif location == 'downstairs':
    name = 'climate.downstairs'
    saved = 'input_number.downstairs_setpoint'
    good=1
else:
    logger.error("Set temperature called for bad location {}.".format(location))

if good:
    # set the temperature
    if not debug:
        # Make the adjustment
        new_setpoint = setpoint
        setpoint_arg = {'entity_id': saved,
                        'value': new_setpoint}
        hass.services.call('input_number', 'set_value', setpoint_arg)
        # logger.info('{} set to {}'.format(saved, new_setpoint))
        new_setpoint_arg = {'entity_id': name, 'temperature': new_setpoint}
        hass.services.call('climate', 'set_temperature', new_setpoint_arg)
        saved_setpoint = new_setpoint
        # logger.info('{} set to {}'.format(name, saved_setpoint))
    else:
        logger.info("Debug mode. No change made.")
