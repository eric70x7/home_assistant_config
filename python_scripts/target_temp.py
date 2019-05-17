#
# set the temperature to to the target temp
#

#
# Set the temperature and update the saved setpoint
#
def set_temp(name, saved, hass, logger, debug, setpoint):
    if not debug:
        # Make the adjustment
        new_setpoint = setpoint
        setpoint_arg = {'entity_id': saved,
                        'value': new_setpoint}
        hass.services.call('input_number', 'set_value', setpoint_arg)
        logger.info('{} set to {}'.format(saved, new_setpoint))
        new_setpoint_arg = {'entity_id': name, 'temperature': new_setpoint}
        hass.services.call('climate', 'set_temperature', new_setpoint_arg)
        saved_setpoint = new_setpoint
        logger.info('{} set to {}'.format(name, saved_setpoint))
        # hass.services.call('wink','refresh_state_from_wink',{})
    else:
        logger.info("Debug mode. No change made.")
    
# debug mode is default
debug = int(data.get('debug', 1))

target_temp = int(float(hass.states.get('input_number.target_temp').state)) # 70

logger.info("Setting target to {}.".format(target_temp))

set_temp('climate.upstairs',
         'input_number.upstairs_setpoint',
         hass,
         logger,
         debug,
         target_temp)

set_temp('climate.downstairs',
         'input_number.downstairs_setpoint',
         hass,
         logger,
         debug,
         target_temp)
