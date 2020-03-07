#
# Set a temperature
#

# debug mode is default
debug = int(data.get('debug', 1))
# name can be upstairs or downstairs
location = data.get('location')
setpoint = data.get('setpoint')

if location == 'upstairs':
    thermostat_id = 'climate.trane_corporation_model_tzemt524aa21ma_mode_2'
elif location == 'downstairs':
    thermostat_id = 'climate.trane_corporation_model_tzemt524aa21ma_mode'
else:
    logger.error("Set temperature called for bad location {}.".format(location))

thermostat = hass.states.get(thermostat_id)
attributes = thermostat.attributes.copy()
attributes['target_temp_high'] = setpoint
# logger.info('{}'.format(attributes))

# set the temperature
if not debug:
    # Make the adjustment
    hass.states.set(thermostat_id, thermostat.state, attributes)
else:
    logger.info("Debug mode. No change made.")
