#
# get_thermostat_id.py
#

thermostat_id=''

location = data.get('location')

if location == 'upstairs':
    thermostat_id = 'climate.trane_corporation_model_tzemt524aa21ma_mode_2'
elif location == 'downstairs':
    thermostat_id = 'climate.trane_corporation_model_tzemt524aa21ma_mode'
else:
    logger.error("get_thermostat_id bad location {}.".format(location))
    
return thermostat_id
