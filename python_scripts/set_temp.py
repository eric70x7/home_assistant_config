#
# Set a temperature
#
# NOTE: this sets the target_temp_high (AC setpoint) and leaves the heat setpoint alone

# debug mode is default
debug = int(data.get('debug', 1))
# name can be upstairs or downstairs
location = data.get('location')
setpoint = data.get('setpoint')
set_heat = data.get('set_heat', 0)

if location == 'upstairs':
    thermostat_id = 'climate.trane_corporation_model_tzemt524aa21ma_mode_2'
elif location == 'downstairs':
    thermostat_id = 'climate.trane_corporation_model_tzemt524aa21ma_mode'
else:
    logger.error("Set temperature called for bad location {}.".format(location))

# set the temperature
if not debug:
    # Get the current low setpoint
    low_setpoint=hass.states.get(thermostat_id).attributes['target_temp_low']
    high_setpoint=hass.states.get(thermostat_id).attributes['target_temp_high']

    if set_heat:
        low_setpoint=setpoint
        logger.info("Set heat to {}.".format(low_setpoint))
    else:
        high_setpoint=setpoint
        logger.info("Set cool to {}.".format(high_setpoint))
    
    # Make the adjustment
    hass.services.call('climate','set_temperature',{'entity_id':thermostat_id,
                                                    'target_temp_high': high_setpoint,
                                                    'target_temp_low': low_setpoint})
else:
    logger.info("Debug mode. No change made.")
