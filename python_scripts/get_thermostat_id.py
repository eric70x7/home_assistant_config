#
# get_thermostat_id.py
#

thermostat_id=''

location = data.get('location')

if location == 'upstairs':
    thermostat_id = 'climate.upstairs_trane_thermostat'
elif location == 'downstairs':
    thermostat_id = 'climate.downstairs_trane_thermostat'
else:
    logger.error("get_thermostat_id bad location {}.".format(location))
    
return thermostat_id
